# subset-b-005165 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/surface_charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/surface_charger.c

## Purpose
`surface_charger.c` exposes the AC adapter state on 7th-generation Microsoft Surface devices through the Surface System Aggregator Module (SSAM). It registers a `POWER_SUPPLY_TYPE_MAINS` device named from match data, currently `ADP1`, and translates SSAM battery `_STA` and power-source requests into a standard `POWER_SUPPLY_PROP_ONLINE` property.

## Important APIs, Types, And Functions
The file is built around SSAM request helpers `ssam_bat_get_sta` and `ssam_bat_get_psrc`, `struct spwr_ac_device`, `struct spwr_psy_properties`, and an `ssam_event_notifier`. `spwr_ac_update_unlocked()` refreshes cached adapter state under `ac->lock`; `spwr_ac_recheck()` updates state and emits `power_supply_changed()` on transitions; `spwr_notify_ac()` handles SSAM battery adapter events; `spwr_ac_get_property()` serves the power-supply core. Probe uses `ssam_device_get_match_data()`, `devm_power_supply_register()`, and `ssam_device_notifier_register()`.

## Control Flow
Probe fetches match properties, allocates `spwr_ac_device`, initializes the notifier and power-supply descriptor, validates the SSAM battery device via `_STA`, registers the mains supply, then subscribes to SSAM adapter-change events. Runtime property reads lock the device, synchronously query `_PSR`, update the cached little-endian state, and return online as a boolean. SSAM event delivery logs the event, accepts all targets and instances for command `SAM_EVENT_CID_BAT_ADP`, rechecks state, and maps any error to an SSAM notifier return. Resume also calls `spwr_ac_recheck()` to refresh userspace after sleep.

## State, Persistence, And Dependencies
Persistent runtime state is only the cached `__le32 state`, the notifier registration, and power-supply registration; no nonvolatile state is written. A mutex protects `state`. The driver depends on the SSAM bus/device framework, SSAM event registry semantics, power-supply class, and Surface BAT target-category commands.

## Integration Points
It supplies batteries named `BAT1` and `BAT2`, uses `module_ssam_device_driver()`, and matches `SSAM_SDEV(BAT, SAM, 0x01, 0x01)`. Its PM hook is a resume refresh, not a suspend action. Removal unregisters the SSAM notifier; devm resources release the supply and memory.

## Risks
`spwr_ac_get_property()` returns early for any nonzero `spwr_ac_update_unlocked()` value, so a successful state change (`status > 0`) can make an `ONLINE` read return `1` instead of filling `val`; this is worth checking against the intended "changed" convention. Listening to all event target/instance pairs is intentional but can overnotify. The state is only as accurate as synchronous SSAM command success; transient command failures propagate to sysfs reads.

## Test Signals
Exercise probe rejection on bad `_STA`, normal registration with `ADP1`, `ONLINE` reads across `_PSR` zero/nonzero values, SSAM adapter event delivery with varied target/instance ids, notifier unregister on remove, and resume-triggered `power_supply_changed()` after a state transition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/surface_charger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/test_power.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/test_power.c

## Purpose
`test_power.c` is a synthetic power-supply driver used to exercise power-supply core behavior from module parameters. It registers AC, USB, and battery supplies with adjustable online, status, health, capacity, voltage, current, charge type, charge behavior, and optional extension properties.

## Important APIs, Types, And Functions
Key data is stored in file-scope module parameters such as `ac_online`, `usb_online`, `battery_status`, `battery_capacity`, `battery_charge_behaviour`, and `battery_extension`. `test_power_get_*_property()` callbacks expose AC, USB, and battery properties. `test_power_set_battery_property()` validates bitmasks in `power_supply_desc` before setting charge behavior/type. `test_power_battery_ext*()` implements a `struct power_supply_ext` for manufacture year, max temperature, and `TIME_TO_EMPTY_NOW`. Parameter handlers use `struct kernel_param_ops`, `map_get_value()`, `map_get_key()`, and `power_supply_changed()`.

## Control Flow
Module init registers three supplies from `test_power_desc[]` and `test_power_configs[]`, then registers the battery extension by default. Reads return static or parameter-backed values. Module parameter writes parse string maps or integers, update globals, and notify the corresponding supply after initialization. The battery extension parameter toggles `power_supply_register_extension()` and `power_supply_unregister_extension()`. Module exit forces AC/USB off, sends change events, sleeps 10 seconds to let observers see the event, unregisters supplies, and clears `module_initialized`.

## State, Persistence, And Dependencies
All state is volatile module-global memory. There is no locking around parameter updates or property reads, so it relies on simple integer/bool stores being adequate for a test fixture. It depends on the power-supply core, module parameter infrastructure, generated `UTS_RELEASE`, and extension APIs.

## Integration Points
The AC and USB supplies list `test_battery` as a supplicant. The battery descriptor advertises writable charge behavior and charge type masks and exposes extension-backed properties when enabled. It is not bound to hardware or firmware.

## Risks
Several `param_get_battery_*()` functions use `map_ac_online` instead of their matching maps, so status/health/presence/technology reads can report `unknown` or wrong strings even when writes succeeded. `param_set_battery_present()` notifies `TEST_AC` rather than the battery. `test_power_configure_battery_extension()` sets `battery_extension = enable` even if unregistering an extension that may not be registered or after registration failure paths, so parameter state can diverge from extension state. Lack of locking can expose races during concurrent parameter writes and property reads, acceptable only for testing.

## Test Signals
Load/unload the module and monitor uevents, verify all advertised properties, write valid and invalid charge behavior/type values, toggle `battery_extension`, validate parameter string maps, confirm `power_supply_changed()` fires only after initialization, and specifically test the suspicious getter maps and presence-notification target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/test_power.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/tps65090-charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/tps65090-charger.c

## Purpose
`tps65090-charger.c` is the TPS65090 charger child driver. It exposes AC presence as `tps65090-ac`, configures PMIC charger registers, optionally enables low-current charging, and handles VAC presence either by IRQ or by a fallback polling kthread.

## Important APIs, Types, And Functions
`struct tps65090_charger` stores parent device, online state, IRQ or poll task, passive-mode flag, power-supply pointer, and platform data. Register helpers from `linux/mfd/tps65090.h` are used by `tps65090_low_chrg_current()`, `tps65090_enable_charging()`, and `tps65090_config_charger()`. `tps65090_charger_isr()` is both the threaded IRQ handler and polling body. DT parsing recognizes `ti,enable-low-current-chrg`.

## Control Flow
Probe obtains parent platform data or DT-derived charger data, allocates state, registers the mains supply, gets an optional IRQ, configures charger registers unless in passive mode, checks initial charger status, enables charging when status indicates presence, and either requests a threaded IRQ or starts `ktps65090charger`. The ISR reads charger status, waits 75 ms, reads interrupt status, sets `ac_online`, enables charging when VACG is set, clears interrupts in active mode, and notifies userspace on online transitions. Remove stops the poll thread when no IRQ was available.

## State, Persistence, And Dependencies
Runtime state is `ac_online`, `prev_ac_online`, `passive_mode`, IRQ id, and optional kthread. Persistent hardware state includes charger-enable, low-current/no-termination, interrupt-mask, and interrupt-status registers. The driver depends on the TPS65090 MFD parent, platform data from the parent cell, optional OF child data, kthreads/freezer, and power-supply class.

## Integration Points
It is registered as platform driver `tps65090-charger` and matches `ti,tps65090-charger`. The parent MFD supplies the register accessors and likely the IRQ resource. `supplied_to` and fwnode metadata come from platform data/firmware.

## Risks
When no IRQ is present, `passive_mode` is set only after `tps65090_config_charger()` and initial status handling, so early register writes still occur even though later polling runs passive. `tps65090_charger_isr()` reads `CG_STATUS1` but uses only `INTR_STS` to decide VAC state; polling with no IRQ may misinterpret sticky interrupt status. `prev_ac_online` is updated only on property read and ISR entry paths, so notifications can be tied to userspace read timing. The ISR sleeps, so it must remain threaded or kthread-only.

## Test Signals
Validate platform-data and DT probes, low-current register programming, initial status detection, IRQ and no-IRQ polling paths, freezer behavior, transition notifications, interrupt clearing, and remove-time kthread shutdown. Hardware tests should include AC plug/unplug with both sticky and cleared interrupt statuses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/tps65090-charger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/tps65217_charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/tps65217_charger.c

## Purpose
`tps65217_charger.c` exposes the TPS65217 charger as a `POWER_SUPPLY_TYPE_MAINS` supply named `tps65217-charger`. It monitors AC/USB source presence and enables the charger when either source is present.

## Important APIs, Types, And Functions
`struct tps65217_charger` holds the MFD pointer, device, power supply, online state, previous state, and optional poll task. `tps65217_config_charger()` programs the NTC type bit, `tps65217_enable_charging()` sets `CHG_EN`, `tps65217_charger_irq()` reads status and active charger state, and `tps65217_charger_poll_task()` provides fallback polling. It uses MFD helpers `tps65217_reg_read()`, `tps65217_set_bits()`, and `tps65217_clear_bits()`.

## Control Flow
Probe allocates state, registers the power supply, resolves USB and AC IRQs by name, configures the charger, and chooses polling if either IRQ is missing. With both IRQs available, it requests shared threaded IRQ handlers and invokes the handler to seed current state. The handler reads `TPS65217_REG_STATUS`, enables charging when AC or USB power bits are present, clears `online` otherwise, emits a change event on transitions, and logs the active bit from `CHGCONFIG0`.

## State, Persistence, And Dependencies
State is volatile `online`, `prev_online`, and optional poll kthread. Hardware state persists in `CHGCONFIG1` NTC and charger-enable bits. Dependencies are the TPS65217 MFD core, named IRQ resources `"USB"` and `"AC"`, kthread/freezer support, and power-supply core.

## Integration Points
The platform driver matches `ti,tps65217-charger`; parent drvdata provides `struct tps65217`. The power supply only exposes `ONLINE`, so policy for current/voltage/health is elsewhere.

## Risks
If either of the two IRQs is unavailable, both are ignored and polling is used. The code sets 100k NTC according to one datasheet note while comments document conflicting datasheet information; board validation is needed. In the IRQ path, current state is checked inside the loop once per IRQ registration, causing duplicate initial reads. No explicit locking protects `online` against sysfs reads while IRQ/poll updates.

## Test Signals
Test AC-only, USB-only, both-source, and no-source states; missing IRQ fallback; kthread stop on remove; NTC configuration failures; charger-enable write failures; and userspace notifications on source transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/tps65217_charger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/twl4030_charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/twl4030_charger.c

## Purpose
`twl4030_charger.c` drives the TWL4030/TPS65950 Battery Charger Interface. It registers separate AC and USB power supplies, configures automatic or linear charging paths, handles backup-battery charging, responds to charger/BCI IRQs and USB PHY notifications, and manages dynamic input-current limits.

## Important APIs, Types, And Functions
`struct twl4030_bci` contains the AC/USB supplies, USB PHY notifier, IRQs, work items, IIO VAC channel, charge modes, current limits, thresholds, and current-ramp state. Register helpers include `twl4030_clear_set()`, `twl4030_bci_read()`, `twl4030_clear_set_boot_bci()`, `twl4030bci_read_adc_val()`, `regval2ua()`, and `ua2regval()`. Core policy functions are `twl4030_charger_update_current()`, `twl4030_charger_enable_usb()`, `twl4030_charger_enable_ac()`, `twl4030_charger_enable_backup()`, `twl4030_bci_get_property()`, and `twl4030_bci_set_property()`.

## Control Flow
Probe initializes default thresholds and charge modes, requests the optional VAC IIO channel and optional USB transceiver, registers `twl4030_ac` and `twl4030_usb`, requests charger-present and BCI threaded IRQs, unmasks BCI monitor interrupts, creates per-supply `mode` sysfs attributes, enables AC charging, processes the initial USB PHY event or disables USB, and configures backup charging from platform data/DT. Charger-present IRQ resets AC current, updates registers, and notifies both supplies. BCI IRQ reads interrupt status registers, notifies on charger-state changes, updates current, and logs fault conditions. USB PHY notifications set target current and schedule work to enable/disable USB charging. A delayed worker ramps USB current in 20 mA steps while VBUS stays above 4.75 V.

## State, Persistence, And Dependencies
Volatile state includes current thresholds, target/current USB limit, AC active flag, charge mode selections, USB event, and workqueue state. Persistent hardware state spans PM master boot BCI bits, main-charge threshold/current registers, watchdog keys, BCI mode keys, backup charger config, and interrupt masks. Dependencies include TWL MFD I2C access, power-supply core, IIO for VAC, USB PHY notifier/runtime PM, platform/DT data, and IRQ resources.

## Integration Points
The platform driver `twl4030_bci` matches `ti,twl4030-bci`. It consumes DT backup properties `ti,bb-uvolt` and `ti,bb-uamp`, a `vac` IIO channel, and the sibling `ti,twl4030-usb` PHY. It exposes `STATUS`, `ONLINE`, `VOLTAGE_NOW`, `CURRENT_NOW`, and writable `INPUT_CURRENT_LIMIT` on both AC and USB plus a custom `mode` sysfs file with `off`, `auto`, and `continuous`.

## Risks
There is minimal locking around shared state touched by IRQs, sysfs stores, USB notifier work, and delayed current work. Several register writes in the USB linear path overwrite `ret` without checking each intermediate result. `twl4030_bci_get_property()` has confusing `INPUT_CURRENT_LIMIT` branch conditions and reads `BCIIREF1` with the two-byte ADC helper, which should be validated. Remove disables charging and masks interrupts but does not explicitly cancel pending work/delayed work before devm teardown. The `allow_usb` module parameter changes default draw policy globally.

## Test Signals
Test AC and USB plug/unplug, USB PHY events, `mode` sysfs transitions, current-limit writes and ramp-back on VBUS sag, VAC IIO absence/defer paths, backup charger DT programming, BCI fault IRQ logging, remove with pending work, and high-current CGAIN transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/twl4030_charger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/twl4030_madc_battery.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/twl4030_madc_battery.c

## Purpose
`twl4030_madc_battery.c` is a simple Li-Ion battery monitor using TWL4030 MADC/IIO channels. It estimates charge state from platform-provided voltage calibration curves and exposes a battery power-supply device.

## Important APIs, Types, And Functions
`struct twl4030_madc_battery` stores the power supply, platform calibration data, and IIO channels for temperature, charge current, and battery voltage. `madc_read()` wraps `iio_read_channel_processed()`. `twl4030_madc_bat_get_*()` helpers read voltage/current/temp/status. `twl4030_madc_bat_voltscale()` selects charging or discharging calibration and linearly interpolates capacity. `twl4030_madc_bat_get_property()` implements the battery property set.

## Control Flow
Probe allocates state, obtains `temp`, `ichg`, and `vbat` IIO channels, sorts charging/discharging calibration tables descending by voltage, stores platform data, and registers `twl4030_battery`. Property reads synchronously sample IIO channels, derive charging status from positive `ichg`, interpolate capacity, estimate charge and time-to-empty, and return fixed technology/presence.

## State, Persistence, And Dependencies
State is mostly platform calibration data plus IIO channel handles. Probe mutates the platform calibration arrays in-place by sorting them. There is no persisted state and no polling worker. Dependencies are platform data from `linux/power/twl4030_madc_battery.h`, IIO channels, sorting helpers, and power-supply core.

## Integration Points
The platform driver binds as `twl4030_madc_battery`. The descriptor uses `external_power_changed = power_supply_changed`, making external supply notifications trigger a battery change event without internal recalculation storage.

## Risks
Probe assumes non-NULL platform data; dereferencing `pdata` would fail if the platform omits it. Calibration arrays must include a sentinel with negative voltage; malformed arrays can read out of bounds. Charge status treats any `ichg` read error as non-charging because `madc_read() > 0` is false. Time-to-empty uses a fixed 400 mA discharge assumption and may be only a coarse estimate.

## Test Signals
Validate all IIO channel acquisition paths, sorted calibration interpolation at table bounds and between points, error handling for channel read failures, missing/malformed platform data, charging-vs-discharging curves, and unit conversions for voltage/current/temp/charge.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/twl4030_madc_battery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/twl6030_charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/twl6030_charger.c

## Purpose
`twl6030_charger.c` exposes the TWL6030/TWL6032 USB charger as a power-supply device. It configures charge voltage/current from battery information, monitors USB VBUS and charger status registers, refreshes the watchdog, and supports writable input-current limits.

## Important APIs, Types, And Functions
`struct twl6030_charger_info` stores the USB power supply, battery info, IRQ, VUSB IIO channel, delayed watchdog work, input-current limit, and chip variant flag. `twl6030_config_cinlimit_reg()` encodes input limits. `twl6030_enable_usb()` programs charge current, watchdog, input limit, voltage regulation, termination, and charger-enable. `twl6030_charger_interrupt()` handles VBUS/charger events. `twl6030_charger_wdg()` periodically rewrites `CONTROLLER_WDG`. Power-supply callbacks are `twl6030_charger_usb_get_property()`, `set_property()`, and `property_is_writeable()`.

## Control Flow
Probe allocates state, gets variant data (`twl6030` or `twl6032`), optionally acquires `vusb` IIO, registers `twl6030_usb`, reads battery info, fills missing voltage/current limits from chip registers, validates ranges, registers autocancel delayed work and a threaded IRQ, clears charger control, then manually invokes the interrupt handler to seed state and enable charging when VBUS is present. The IRQ reads controller and charger status registers, emits a power-supply change, enables USB charging and watchdog work on VBUS detect, and cancels watchdog work on VBUS removal. Property reads report charger status, VUSB voltage, online state, and current limit.

## State, Persistence, And Dependencies
Runtime state includes input-current limit, delayed work scheduling, battery info, VUSB channel, and variant flag. Hardware state is in TWL main-charge registers for current, voltage, input limit, watchdog, and controller enable. Dependencies are TWL MFD I2C helpers, power-supply battery-info parsing, IIO, devm delayed-work helpers, IRQ resources, and OF match data.

## Integration Points
The platform driver matches `ti,twl6030-charger` and `ti,twl6032-charger`; TWL6032 enables extended input-current encoding. It exposes a single USB supply with `STATUS`, `ONLINE`, `VOLTAGE_NOW`, and writable `INPUT_CURRENT_LIMIT`.

## Risks
`twl6030_enable_usb()` writes `CHARGERUSB_CINLIMIT` twice, first through the generic encoder and then fixed 500 mA, so a caller-specified or extended limit can be overwritten during enable. Voltage validation checks `< 350000` instead of likely `< 3500000`, allowing invalid sub-3.5 V values through. `property_is_writeable()` logs at info level on every query, which can be noisy. IRQ and property reads are unsynchronized with writes to `input_current_limit`.

## Test Signals
Test TWL6030 vs TWL6032 current-limit encodings, battery-info missing/default paths, invalid charge voltage/current/termination values, VBUS attach/detach IRQs, watchdog rescheduling/cancelation, VUSB IIO absence, writable input-current-limit behavior after enable, and status mapping for full/current-termination/charging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/twl6030_charger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/ucs1002_power.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/ucs1002_power.c

## Purpose
`ucs1002_power.c` drives the Microchip/SMSC UCS1002 programmable USB port power controller. It exposes the port as a USB power-supply device and a fixed 5 V VBUS regulator, reporting attachment, delivered charge/current, current limit, USB charging type, and health.

## Important APIs, Types, And Functions
`struct ucs1002_info` holds I2C/regmap state, power-supply pointer, regulator descriptor/device, presence/health state, output-disable flag, and delayed health poll. Property helpers include `ucs1002_get_online()`, `ucs1002_get_charge()`, `ucs1002_get_current()`, `ucs1002_get_max_current()`, `ucs1002_set_max_current()`, `ucs1002_set_usb_type()`, and `ucs1002_get_usb_type()`. IRQ handlers are `ucs1002_charger_irq()` for attach detect and `ucs1002_alert_irq()` for health polling. Regulator operations wrap regmap enable/disable.

## Control Flow
Probe creates an 8-bit regmap, reads DT IRQs `a_det` and `alert`, verifies product ID `0x4e`, enables charge rationing, ignores mode pins and defaults active mode to BC1.2 CDP, sets a safe 500 mA current limit, registers the USB power supply, reads pin status to determine regulator enable polarity, registers the VBUS regulator, initializes health state and delayed work, then requests optional attach and alert IRQs. Property reads pull live register values or cached `present`/`health`; writable properties update current-limit and active USB mode registers.

## State, Persistence, And Dependencies
The chip keeps persistent/current hardware state in general config, switch config, current limit, accumulated charge, and status registers. Driver state caches health, present, and output-disable. It depends on I2C, regmap, OF IRQ naming, regulator framework, power-supply USB type APIs, and delayed work.

## Integration Points
It matches `microchip,ucs1002`. The regulator named `ucs1002-vbus` shares the same switch config register as the power-supply current limit and uses DT regulator constraints. `CURRENT_MAX=0` intentionally disables output logically until a nonzero current limit restores it.

## Risks
`regmap_bulk_read()` reads a `u32` into native memory and then applies `be32_to_cpu`; this assumes regmap bulk byte order and alignment match the charge-register layout. `ucs1002_set_max_current()` disables via `info->rdev` before checking that `rdev` is registered; current probe calls it before regulator registration with nonzero current, but future callers should preserve that ordering. `present` is initialized only by IRQ, not a synchronous probe read. Health polling only reschedules while error state remains bad and relies on alert IRQs to restart.

## Test Signals
Validate product-ID mismatch, default mode/current programming, all current-limit values and rejection of unsupported values, `CURRENT_MAX=0` regulator interaction, USB type set/get mappings, charge/current unit conversions, attach IRQ notification, alert-to-health mapping, missing IRQ operation, and regulator polarity from `F_SEL_PIN`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/ucs1002_power.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/ug3105_battery.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/ug3105_battery.c

## Purpose
`ug3105_battery.c` is an I2C battery monitor driver for the uPI uG3105. It uses voltage/current ADC readings with `adc-battery-helper` to expose battery properties, but intentionally does not use the coulomb counter because Linux cannot guarantee reads while powered off or suspended.

## Important APIs, Types, And Functions
`struct ug3105_chip` embeds `struct adc_battery_helper` as its first member, stores the I2C client, power supply, and ADC scaling factors. `ug3105_read_word()` wraps SMBus word reads. `ug3105_get_voltage_and_current_now()` reads voltage and signed current registers and converts them to microvolts/microamps. `ug3105_start()` enters run mode and resets the coulomb counter; `ug3105_stop()` enters standby. Probe initializes scale factors and calls `adc_battery_helper_init()`.

## Control Flow
Probe allocates state, starts the chip, reads optional `upisemi,rsns-microohm` with a default 10 mOhm sense resistor, computes voltage/current units, registers `ug3105_battery`, initializes the helper, and stores client data. Suspend calls helper suspend then stops the chip; resume restarts the chip and resumes helper polling. Remove and shutdown stop the chip.

## State, Persistence, And Dependencies
Driver state is scale factors and helper state. Hardware state is the mode register and reset coulomb counter. The coulomb counter is reset at start and not accumulated. Dependencies are I2C SMBus, `adc-battery-helper`, power-supply core, firmware property reading, and PM ops.

## Integration Points
The descriptor delegates property implementation to `adc_battery_helper_get_property()` and external-power handling to `adc_battery_helper_external_power_changed()`. It binds via I2C id `"ug3105"` and has PM hooks.

## Risks
The voltage scaling includes a documented empirical factor of 10; board-specific validation is important. Resetting the coulomb counter on each start loses accumulated charge data by design. `ug3105_start()`/`stop()` ignore SMBus write failures. The module author string is missing a closing angle bracket, a metadata issue rather than runtime behavior.

## Test Signals
Test probe with default and custom sense resistor, signed current conversion, voltage scaling against measured values, helper property polling, suspend/resume stop/start behavior, remove/shutdown standby writes, and I2C read failures propagated through property reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/ug3105_battery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/wilco-charger.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/wilco-charger.c

## Purpose
`wilco-charger.c` exposes Wilco EC charge-control settings through a power-supply device. It maps EC byte properties for charge mode and charge start/end thresholds to standard power-supply charge type and charge-control threshold properties.

## Important APIs, Types, And Functions
Property IDs are `PID_CHARGE_MODE`, `PID_CHARGE_LOWER_LIMIT`, and `PID_CHARGE_UPPER_LIMIT`. `enum charge_mode` defines EC modes. `psp_val_to_charge_mode()` and `charge_mode_to_psp_val()` convert between power-supply values and EC values. `wilco_charge_get_property()` and `wilco_charge_set_property()` call `wilco_ec_get_byte_property()`/`wilco_ec_set_byte_property()`. The descriptor `wilco_ps_desc` exposes three writable properties.

## Control Flow
Probe retrieves the parent `wilco_ec_device`, sets it as power-supply drvdata, and registers a mains-type supply named `wilco-charger`. Reads select the EC property id, fetch a byte, and convert charge mode if needed. Writes validate charge mode or threshold ranges and update the EC property.

## State, Persistence, And Dependencies
The driver holds no private state; all persistence lives in the EC. It depends on the Wilco EC platform data API and power-supply core.

## Integration Points
The platform driver name and alias are `wilco-charger`. Userspace sees `CHARGE_TYPE`, `CHARGE_CONTROL_START_THRESHOLD`, and `CHARGE_CONTROL_END_THRESHOLD`, matching ABI docs referenced in the file header.

## Risks
`wilco_charge_property_is_writeable()` returns true for every property the core asks about, not just the three descriptor properties; current descriptor scope makes this low risk. Start and end thresholds are individually range-checked but not cross-validated, so userspace might set a start threshold greater than or equal to the end threshold if the EC does not reject it. Unknown EC charge-mode values return `-EBADMSG`.

## Test Signals
Test all charge-mode round trips, invalid mode and threshold writes, EC communication errors, unknown raw EC mode handling, start/end threshold ordering at the EC level, and power-supply registration with missing parent drvdata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/wilco-charger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/wm831x_backup.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/wm831x_backup.c

## Purpose
`wm831x_backup.c` exposes the WM831x backup battery charger as a battery power-supply device. It optionally configures backup charging from platform data and reports status, voltage, and presence.

## Important APIs, Types, And Functions
`struct wm831x_backup` holds the parent PMIC, power-supply handle, descriptor, and generated name. `wm831x_config_backup()` validates and programs backup charger enable, detection, voltage limit, current limit, and constant-voltage mode. `wm831x_backup_read_voltage()` uses AUXADC. `wm831x_backup_get_prop()` reads `WM831X_BACKUP_CHARGER_CONTROL` and serves properties.

## Control Flow
Probe obtains the parent `struct wm831x`, allocates state, calls `wm831x_config_backup()` while tolerating configuration failures, constructs a per-PMIC or default name, fills the descriptor, and registers the supply. Property reads first read the backup charger control register, then report charging status, AUXADC backup voltage, or present based on the charger-status bit.

## State, Persistence, And Dependencies
Driver state is just the descriptor and parent pointer. Hardware state persists in the backup charger control register. Dependencies include WM831x core register locking/unlocking, AUXADC, platform data, and power-supply core.

## Integration Points
The platform driver name is `wm831x-backup`. It is an MFD child of a WM831x PMIC and uses `wm831x_pdata->backup` when available.

## Risks
Configuration failures are intentionally nonfatal, which can leave hardware in bootloader/default state while still registering a readable supply. `PRESENT` is inferred from `WM831X_BKUP_CHG_STS`, which may indicate charger activity rather than physical cell presence. Invalid voltage/current platform values log errors but do not fail probe.

## Test Signals
Validate platform data combinations, invalid `vlim`/`ilim` logging, register unlock failure, AUXADC read failure, status/presence mapping, multiple PMIC naming, and operation when no backup config is provided.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/wm831x_backup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/wm831x_power.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/wm831x_power.c

## Purpose
`wm831x_power.c` is the main WM831x PMIC power-supply driver. It registers wall, USB, and optionally battery supplies; configures the battery charger from platform data; reports source/voltage/health/charge state; handles PMIC IRQs; and optionally tracks USB PHY current-limit notifications.

## Important APIs, Types, And Functions
`struct wm831x_power` stores parent PMIC, supply handles/descriptors/names, battery-present flag, USB PHY, and notifier. Wall/USB helpers use `wm831x_power_check_online()` and `wm831x_power_read_voltage()`. Battery configuration is built from `struct chg_map` tables and `wm831x_battery_apply_config()` inside `wm831x_config_battery()`. Runtime status helpers are `wm831x_bat_check_status()`, `wm831x_bat_check_type()`, and `wm831x_bat_check_health()`. IRQ handlers include `wm831x_bat_irq()`, `wm831x_syslo_irq()`, and `wm831x_pwr_src_irq()`.

## Control Flow
Probe allocates state, builds names, configures the charger if platform data is present, registers wall and USB supplies, checks `CHARGER_CONTROL_1` to decide whether to register the battery, requests SYSLO, power-source, and eight battery IRQs, and optionally registers a USB PHY notifier from the `phys` phandle. Power-source IRQs notify wall/USB/battery; battery IRQs notify battery if present; USB limit notifications choose the highest supported current limit no greater than the requested limit and update `WM831X_POWER_STATE`.

## State, Persistence, And Dependencies
Runtime state includes descriptors, `have_battery`, IRQ registrations, and optional USB notifier. Hardware persistence is in charger control, power state, system status, and charger status registers. Dependencies are WM831x MFD core/AUXADC/PMU headers, platform data, IRQ names from the MFD cell, USB PHY notifier, and power-supply core.

## Integration Points
The platform driver is `wm831x-power`. It registers names like `wm831x-wall`, `wm831x-usb`, and `wm831x-battery` with numeric suffixes when platform data provides a PMIC number. Battery is marked `use_for_apm`.

## Risks
Error unwind uses raw `platform_get_irq_byname()` in the battery IRQ loop while registration used `wm831x_irq()`, so failed-probe cleanup may free the wrong Linux IRQ for battery events. The name setup uses `sizeof(power->wall_name)` for battery and USB buffers, currently same size but fragile. Configuration failures are logged but nonfatal. Battery registration is skipped if charger enable is not set after configuration, which can hide a physically present battery when policy disables charging.

## Test Signals
Test charger configuration maps, no-platform-data probe, wall/USB/battery property reads, optional battery registration, all IRQ request/unwind paths, USB PHY notifier current-limit mapping, remove freeing all IRQs, and source-change notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/wm831x_power.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/wm8350_power.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/wm8350_power.c

## Purpose
`wm8350_power.c` registers WM8350 AC, USB, and battery power supplies and configures the WM8350 battery charger. It reports source selection, voltages, battery status/health/charge type, exposes a charger-state sysfs attribute, and handles charger and source IRQs.

## Important APIs, Types, And Functions
Voltage helpers read AUXADC inputs with `WM8350_AUX_COEFF`. `wm8350_get_supplies()` derives active supply bits from state-machine, override, comparator, and charger registers. `wm8350_charger_config()` applies a `wm8350_charger_policy`. `wm8350_batt_status()`, `wm8350_bat_check_health()`, and `wm8350_bat_get_charge_type()` translate PMIC state to power-supply values. `wm8350_charger_handler()` handles many charger/source IRQs. `wm8350_init_charger()` registers IRQs with full unwind.

## Control Flow
Probe registers AC, battery, and USB supplies, creates `charger_state`, registers charger/source IRQs, configures the charger, and enables charging when configuration succeeds. IRQs log faults, notify battery on thermal/start/end/timeout events, configure and enable fast charge when fast-ready fires, and reconfigure/notify all supplies on source changes. Remove frees charger IRQs and removes the sysfs file.

## State, Persistence, And Dependencies
Most state is stored in `wm8350->power` supplied by the MFD core, including policy and supply pointers. Hardware state persists in charger control, power management, state machine, overrides, and AUXADC registers. Dependencies include WM8350 MFD supply/core/comparator APIs and power-supply class.

## Integration Points
The platform driver name is `wm8350-power`. It uses the parent platform drvdata directly and expects `wm8350->power.policy` to be populated by board/MFD code. It exports `wm8350-ac`, `wm8350-usb`, and `wm8350-battery`.

## Risks
`wm8350_power_probe()` ignores the return value from `wm8350_init_charger()`, so supplies can register even if IRQ setup failed. It also returns success after `device_create_file()` failure by resetting `ret` to zero. Missing charger policy makes configuration return `-EINVAL`, but supplies still exist. `wm8350_batt_status()` maps charger-off to discharging even when no battery path is active. IRQ handler reconfiguration depends on policy remaining valid.

## Test Signals
Validate supply detection combinations, policy validation including USB fast limit, charger-state sysfs output, all IRQ registration/unwind paths, ignored IRQ-init failure behavior, source-change reconfiguration, battery health thresholds, and AUXADC read error behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/wm8350_power.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/wm97xx_battery.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/wm97xx_battery.c

## Purpose
`wm97xx_battery.c` is a platform-data-driven WM97xx battery monitor. It reads optional battery voltage and temperature AUX ADC channels, tracks charge/discharge status through an optional GPIO, and exposes only properties supported by board data.

## Important APIs, Types, And Functions
Global objects include `bat_work`, `charge_gpiod`, `work_lock`, `bat_status`, dynamic `prop`, and `bat_psy`. `wm97xx_read_bat()` and `wm97xx_read_temp()` apply platform multipliers/dividers to AUX ADC readings. `wm97xx_bat_get_property()` serves supported properties. `wm97xx_bat_update()` samples the charge GPIO and emits change events. `wm97xx_chrg_irq()` and `external_power_changed` schedule work.

## Control Flow
Probe requires platform data and singleton device id `-1`, gets an optional charge GPIO, counts supported properties from platform fields, allocates the property array, initializes work, assigns a supplied or fallback battery name, registers the power supply, schedules an initial update, and requests a GPIO IRQ when present. Work updates status based on GPIO value; suspend flushes work and resume reschedules it. Remove frees the GPIO IRQ and cancels work.

## State, Persistence, And Dependencies
The driver uses file-scope singleton state, so it supports only one instance. No hardware state is written. It depends on WM97xx AUX ADC access through the parent, platform data, optional GPIO descriptor/IRQ, workqueues, and power-supply core.

## Integration Points
The platform driver name is `wm97xx-battery`; the parent must provide WM97xx core drvdata and `struct wm97xx_batt_pdata`. `use_for_apm` is enabled for legacy battery reporting.

## Risks
File-scope `bat_psy`, `charge_gpiod`, `bat_status`, and `prop` make multi-instance support impossible and can cause cross-device corruption if that assumption changes. The GPIO polarity is hard-coded as value 0 means charging. `request_irq()` is not devm-managed but remove does free it. `wm97xx_read_bat()`/`temp()` do not guard against zero divisors in platform data.

## Test Signals
Test with and without charge GPIO, all optional property combinations, ADC scaling and invalid divisors, GPIO IRQ status transitions, suspend/resume work behavior, singleton id rejection, missing platform data, and remove while work is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/wm97xx_battery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/powercap/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/powercap/Kconfig

## Purpose
`drivers/powercap/Kconfig` defines configuration options for the generic powercap sysfs framework and its client drivers: Intel RAPL, idle injection, ARM SCMI Powercap, and DTPM backends.

## Important APIs, Types, And Functions
This is Kconfig data rather than C code. `menuconfig POWERCAP` gates the subtree. `INTEL_RAPL_CORE` is a hidden tristate selected by MSR/TPMI RAPL drivers. `IDLE_INJECT`, `ARM_SCMI_POWERCAP`, `DTPM`, `DTPM_CPU`, and `DTPM_DEVFREQ` define build-time inclusion and dependencies.

## Control Flow
If `POWERCAP` is disabled, all nested options are unavailable. Enabling Intel MSR or TPMI RAPL selects `INTEL_RAPL_CORE`. `DTPM_CPU` and `DTPM_DEVFREQ` depend on `DTPM` and `ENERGY_MODEL`; CPU additionally requires SMP. `IDLE_INJECT` depends on CPU idle support. `ARM_SCMI_POWERCAP` depends on SCMI protocol support.

## State, Persistence, And Dependencies
The file persists no runtime state; it controls compile-time objects. Dependencies directly align with subsystem integration points: PCI/IOSF for Intel RAPL core, x86 and TPMI for Intel interfaces, CPU_IDLE for idle injection, ARM_SCMI_PROTOCOL for SCMI, OF/ENERGY_MODEL/SMP for DTPM.

## Integration Points
The selected symbols are consumed by the Makefile in the same directory and by conditional compilation in `dtpm_subsys.h`.

## Risks
`DTPM` is marked experimental in the prompt text but has no explicit `depends on EXPERT` or warning gate. `INTEL_RAPL_CORE` depends on PCI and selects IOSF_MBI, so build coverage should include both MSR and TPMI paths. `IDLE_INJECT` is bool only, reflecting early init/per-CPU thread design.

## Test Signals
Build-test representative configs: `POWERCAP=n`, Intel MSR, Intel TPMI, `IDLE_INJECT=y` without CPU_IDLE rejection, `ARM_SCMI_POWERCAP=m`, `DTPM=y` with and without CPU/devfreq backends, and dependency failure cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/powercap/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/powercap/Makefile -->
# sources/distributed-fs/ceph-client/drivers/powercap/Makefile

## Purpose
`drivers/powercap/Makefile` maps powercap Kconfig symbols to built objects.

## Important APIs, Types, And Functions
It declares `obj-$(CONFIG_DTPM) += dtpm.o`, CPU and devfreq DTPM backends, generic `powercap_sys.o`, Intel RAPL core/MSR/TPMI objects, `idle_inject.o`, and `arm_scmi_powercap.o`.

## Control Flow
Kbuild includes each object when the corresponding config is `y` or `m`, subject to symbol type. `powercap_sys.o` follows `CONFIG_POWERCAP`; DTPM backends are independently gated by their specific symbols.

## State, Persistence, And Dependencies
There is no runtime state. Build state follows Kconfig. Because `DTPM`, `DTPM_CPU`, and `DTPM_DEVFREQ` are bool in Kconfig, their objects are built-in when enabled, not modules.

## Integration Points
The file is the build bridge for the Kconfig options and source files in `drivers/powercap`. It must stay consistent with `dtpm_subsys.h` conditional subsystem list.

## Risks
Missing object entries would silently omit enabled subsystems; current entries cover the visible Kconfig options. Ordering builds generic `dtpm.o` before its backends but link order rarely matters for these symbols in built-in code.

## Test Signals
Run build matrix checks for each config symbol and verify expected objects appear in `drivers/powercap/` build output, especially `CONFIG_POWERCAP=m/y`, Intel RAPL variants, DTPM backend combinations, and SCMI module naming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/powercap/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/powercap/arm_scmi_powercap.c -->
# sources/distributed-fs/ceph-client/drivers/powercap/arm_scmi_powercap.c

## Purpose
`arm_scmi_powercap.c` bridges ARM SCMI Powercap protocol domains into the generic Linux powercap sysfs framework. It registers SCMI firmware-advertised powercap domains as hierarchical powercap zones with one constraint each.

## Important APIs, Types, And Functions
`struct scmi_powercap_zone` wraps SCMI domain info, protocol handle, powercap zone, tree state, and list node. `struct scmi_powercap_root` stores all zones and height-indexed registered lists. Zone callbacks implement measurement, enable get/set, cap get/set, PAI time-window get/set, and min/max reporting through `scmi_powercap_proto_ops`. `scmi_powercap_normalize_cap()` and `_time()` clamp/round user requests to firmware limits. `scmi_zones_register()` registers parent zones before children and tracks heights for reverse unregister.

## Control Flow
Module init registers a powercap control type named `arm-scmi`, then registers an SCMI driver. Probe gets the SCMI Powercap protocol, reads domain count, allocates zone arrays, fetches each domain's info, marks domains with unsupported abstract scale invalid, and calls `scmi_zones_register()`. Registration walks domain relationships, recursing upward through parents before registering a child. Remove unregisters zones from leaves to roots. Module exit unregisters the SCMI driver and control type.

## State, Persistence, And Dependencies
State is the global control type, global protocol-ops pointer, per-device root arrays, per-zone flags, and firmware-backed caps/PAI/enables. No nonvolatile kernel state is persisted; all constraints are forwarded to SCMI firmware. Dependencies include the SCMI core/protocol handle and powercap framework.

## Integration Points
The SCMI id table binds protocol `SCMI_PROTOCOL_POWERCAP` with name `"powercap"`. Each registered zone is named from SCMI domain info and uses the SCMI parent id to build the sysfs hierarchy. Unsupported abstract-scale leaf domains are pruned; unsupported internal domains abort registration.

## Risks
`powercap_ops` is file-global, so multiple SCMI instances with different protocol-op pointers would share it. `scmi_powercap_register_zone()` removes invalid zones from the list but non-leaf invalid zones fail later; hierarchy assumptions rely on protocol validation. `scmi_powercap_get_max_power_range_uw()` returns `U32_MAX` independent of scaling/range. Cap normalization rounds down after clamping; requests just above minimum may round below the minimum if `min_power_cap` is not aligned to `power_cap_step`.

## Test Signals
Test domain trees out of order, multiple root domains, unsupported abstract-scale leaves and internal nodes, cap/time normalization, monitoring-disabled domains, cap/pai config-disabled domains, enable get/set, remove unregister order, SCMI protocol errors, and multiple SCMI device instances if supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/powercap/arm_scmi_powercap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/powercap/dtpm.c -->
# sources/distributed-fs/ceph-client/drivers/powercap/dtpm.c

## Purpose
`dtpm.c` implements the generic Dynamic Thermal Power Management powercap hierarchy. It creates virtual and device-backed powercap zones, aggregates child power, distributes power limits down the tree by weights, and exports hierarchy creation/destruction APIs.

## Important APIs, Types, And Functions
Global state is protected by `dtpm_lock` and includes the powercap control type `pct` and `root`. Public APIs are `dtpm_init()`, `dtpm_register()`, `dtpm_unregister()`, `dtpm_update_power()`, `dtpm_release_zone()`, `dtpm_create_hierarchy()`, and `dtpm_destroy_hierarchy()`. Powercap callbacks include `get_power_uw()`, `set_power_limit_uw()`, `get_power_limit_uw()`, `get_max_power_range_uw()`, and constraint-name helpers. Hierarchy setup uses `dtpm_setup_virtual()`, `dtpm_setup_dt()`, `dtpm_for_each_child()`, and the subsystem table from `dtpm_subsys.h`.

## Control Flow
`dtpm_create_hierarchy()` registers a `dtpm` control type, obtains a platform hierarchy via `of_machine_get_match_data()`, walks child descriptors recursively, creates virtual nodes directly, and asks each enabled subsystem to bind DT nodes as leaves. Leaf nodes provide `dtpm_ops`; virtual nodes aggregate children. Limit writes are clamped to a node's min/max, then `__set_power_limit_uw()` either calls a leaf's `set_power_uw()` or divides the request among children by 1024-based weights. `dtpm_update_power()` subtracts old values from ancestors, refreshes leaf power, restores unconstrained limit to max, adds values back, and rebalances weights.

## State, Persistence, And Dependencies
The framework stores the tree in `struct dtpm` parent/child lists and power values (`power_min`, `power_max`, `power_limit`, `weight`, flags). No nonvolatile state persists. Dependencies are the generic powercap framework, OF machine match data, DTPM backend ops, mutex/list helpers, and exported `linux/dtpm.h` contracts.

## Integration Points
DTPM backends are listed in `dtpm_subsys.h`; CPU and devfreq leaves call `dtpm_register()` and implement ops. Sysfs appears under the `dtpm` powercap control type. Virtual nodes must not have ops; leaves must have complete ops.

## Risks
`set_power_limit_uw()` does not take `dtpm_lock`, so external synchronization is not obvious despite comments saying the node lock must be held. `__set_power_limit_uw()` uses `table[i - 1]` style assumptions in backends and expects valid ranges. If a child limit update fails midway, already-updated siblings are not rolled back. `dtpm_create_hierarchy()` initializes subsystems after hierarchy creation, so backend setup callbacks run before backend init hooks. Destroy assumes `root` is valid when `pct` exists.

## Test Signals
Test single root enforcement, virtual and DT node hierarchy creation, backend setup failures, limit distribution at min/max/intermediate values, weight rebalance after hotplug power updates, failed child set operations, release denial for nodes with children, repeated create/destroy, and sysfs powercap operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/powercap/dtpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/powercap/dtpm_cpu.c -->
# sources/distributed-fs/ceph-client/drivers/powercap/dtpm_cpu.c

## Purpose
`dtpm_cpu.c` implements the CPU backend for DTPM using CPU frequency policies and the Energy Model. It registers one DTPM leaf per cpufreq performance domain and enforces power limits by applying maximum-frequency QoS constraints.

## Important APIs, Types, And Functions
`struct dtpm_cpu` embeds `struct dtpm`, a `freq_qos_request`, and representative CPU id. Per-CPU `dtpm_per_cpu` maps related CPUs to the same leaf. Backend ops are `set_pd_power_limit()`, `get_pd_power_uw()`, `update_pd_power_uw()`, and `pd_release()`. Hotplug callbacks `cpuhp_dtpm_cpu_online()` and `_offline()` call `dtpm_update_power()`. Setup functions include `__dtpm_cpu_setup()` and `dtpm_cpu_setup()`.

## Control Flow
For a DT CPU node, setup maps the node to a CPU, gets its cpufreq policy, rejects missing or artificial energy models, allocates a backend, assigns all related CPUs to the same `dtpm_cpu`, registers a DTPM leaf, and adds a max-frequency QoS request initialized to the highest EM frequency. Limit setting walks EM performance states until power exceeds the requested limit, applies the previous state's frequency through QoS, and returns the achieved power. Current power estimates choose the EM state at or above current cpufreq and scale by scheduler utilization across online CPUs in the domain.

## State, Persistence, And Dependencies
State includes per-domain DTPM node, QoS request, representative CPU, and per-CPU pointers. Power min/max depend on current online CPUs, so hotplug updates the DTPM tree. Dependencies include cpufreq, CPU hotplug, Energy Model, scheduler utilization, OF CPU node mapping, and DTPM core.

## Integration Points
`dtpm_cpu_ops` is included in `dtpm_subsys.h` under `CONFIG_DTPM_CPU`. It registers CPU hotplug states in its init hook and removes them in exit. Leaf names are `cpuN-cpufreq`.

## Risks
`set_pd_power_limit()` indexes `table[i - 1]`; if a requested limit is below the first performance state's power, `i` remains 0 and this underflows. `update_pd_power_uw()` assumes `em_cpu_get()` succeeds after setup and does not recheck. Hotplug-state cleanup calls `cpuhp_remove_state_nocalls(CPUHP_AP_ONLINE_DYN)`, but dynamic online state ids are normally returned by `cpuhp_setup_state()`; storing the returned id would be safer. Power estimation depends on scheduler utilization snapshots and can be approximate.

## Test Signals
Test EM missing/artificial rejection, related-CPU grouping, min-limit and below-min limit behavior, hotplug online/offline power updates, QoS request add/remove, current power scaling under load, DTPM unregister release cleanup, and cpuhp setup failure unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/powercap/dtpm_cpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/powercap/dtpm_devfreq.c -->
# sources/distributed-fs/ceph-client/drivers/powercap/dtpm_devfreq.c

## Purpose
`dtpm_devfreq.c` implements a DTPM backend for devfreq devices with Energy Model data. It registers devfreq devices as DTPM leaves, estimates power from devfreq load/frequency, and limits power through device PM QoS maximum-frequency requests.

## Important APIs, Types, And Functions
`struct dtpm_devfreq` embeds `struct dtpm`, `dev_pm_qos_request`, and a `struct devfreq *`. Backend ops are `update_pd_power_uw()`, `set_pd_power_limit()`, `get_pd_power_uw()`, and `pd_release()`. `_normalize_load()` converts devfreq busy/total time to a 0..1024 scale. `__dtpm_devfreq_setup()` registers Energy Model data if missing, registers the DTPM node, and adds PM QoS.

## Control Flow
During DT setup, the backend finds a devfreq device by node; absent devices are ignored. If no EM exists, it tries `dev_pm_opp_of_register_em()`. It allocates state, initializes DTPM ops, registers a leaf named from the parent device, adds a `DEV_PM_QOS_MAX_FREQUENCY` request, then calls `dtpm_update_power()`. Limit setting chooses the highest EM frequency whose power is not greater than the request, writes QoS, and returns achieved power. Current power uses `devfreq->last_status`, normalizes load, finds the EM frequency at or above current frequency, and scales power by busy fraction.

## State, Persistence, And Dependencies
State is the DTPM node, devfreq pointer, and PM QoS request. Hardware/device state is affected only through PM QoS. Dependencies include devfreq, OPP/EM registration, PM QoS, OF node lookup, and DTPM core.

## Integration Points
`dtpm_devfreq_ops` is included under `CONFIG_DTPM_DEVFREQ`. It is invoked by `dtpm_setup_dt()` for any hierarchy DT node; nodes without devfreq devices are skipped quietly.

## Risks
Like CPU, `set_pd_power_limit()` uses `table[i - 1]` and can underflow if the requested limit is below the lowest EM state. `__dtpm_devfreq_setup()` registers an EM when missing but does not re-fetch `pd` afterward before later functions rely on it. `dtpm_update_power()` return value is ignored after QoS setup. There is no exit hook beyond node release, so backend lifetime depends on DTPM tree destruction.

## Test Signals
Test missing devfreq nodes, missing EM with successful/failed OPP EM registration, min-limit underflow behavior, PM QoS add/remove, load normalization for huge and zero total time, current-frequency unit conversion, and DTPM unregister cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/powercap/dtpm_devfreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/powercap/dtpm_subsys.h -->
# sources/distributed-fs/ceph-client/drivers/powercap/dtpm_subsys.h

## Purpose
`dtpm_subsys.h` declares and assembles the enabled DTPM backend subsystem operations for the generic DTPM core.

## Important APIs, Types, And Functions
It declares `extern struct dtpm_subsys_ops dtpm_cpu_ops;` and `dtpm_devfreq_ops;`, then defines `struct dtpm_subsys_ops *dtpm_subsys[]` with entries conditional on `CONFIG_DTPM_CPU` and `CONFIG_DTPM_DEVFREQ`.

## Control Flow
The DTPM core includes this header and iterates `dtpm_subsys[]` during DT node setup, subsystem initialization, and subsystem exit. Compile-time configuration determines which setup/init/exit hooks are present.

## State, Persistence, And Dependencies
The array is static data in whichever translation unit includes the header, currently `dtpm.c`. There is no runtime mutation. Dependencies are the `struct dtpm_subsys_ops` definition from `linux/dtpm.h` and Kconfig symbols.

## Integration Points
This is the only list connecting generic DTPM hierarchy walking with CPU and devfreq backends. Adding another backend requires a new extern and conditional array entry.

## Risks
Defining a non-`static` array in a header would create duplicate symbols if included by multiple C files. It is currently included by `dtpm.c` only, but future includes could break linkage. The array has no sentinel; all loops use `ARRAY_SIZE(dtpm_subsys)`.

## Test Signals
Build all combinations of `CONFIG_DTPM_CPU` and `CONFIG_DTPM_DEVFREQ`, verify array size and linkage, ensure `dtpm.c` loops handle an empty array, and check no other C file includes this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/powercap/dtpm_subsys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/powercap/idle_inject.c -->
# sources/distributed-fs/ceph-client/drivers/powercap/idle_inject.c

## Purpose
`idle_inject.c` implements the idle injection framework, allowing clients to force selected CPUs into precise idle intervals for a configured portion of a period. It is intended for power capping and thermal control.

## Important APIs, Types, And Functions
`struct idle_inject_thread` stores the per-CPU smpboot task and run flag. `struct idle_inject_device` stores hrtimer, idle/run durations, max latency, optional update callback, and cpumask. Exported APIs are `idle_inject_register_full()`, `idle_inject_register()`, `idle_inject_unregister()`, `idle_inject_set_duration()`, `idle_inject_get_duration()`, `idle_inject_set_latency()`, `idle_inject_start()`, and `idle_inject_stop()`. Internal work uses `idle_inject_wakeup()`, `idle_inject_timer_fn()`, `idle_inject_fn()`, and smpboot callbacks.

## Control Flow
An early initcall registers per-CPU smpboot threads. A client registers a cpumask; registration allocates an `idle_inject_device`, initializes its hrtimer, sets default latency, stores an optional update callback, and claims per-CPU device pointers. Starting verifies nonzero total period, wakes all online CPUs in the mask, and starts a periodic hrtimer. Each timer tick optionally calls `update()`, wakes per-CPU threads, and forwards the timer by run+idle duration. Each woken thread clears its `should_run` flag and calls `play_idle_precise()` for the idle duration with the configured latency. Stop cancels the timer, disables CPU hotplug, clears `should_run` for all CPUs in the mask, waits for tasks to become inactive, and reenables hotplug. Unregister stops, clears per-CPU pointers, and frees the device.

## State, Persistence, And Dependencies
State is per-CPU `idle_inject_thread`, per-CPU `idle_inject_device *`, the allocated control device, and hrtimer. No persistent state exists. Dependencies include smpboot, hrtimer, CPU hotplug locking, scheduler `play_idle_precise()`, RT scheduling setup via `sched_set_fifo()`, and the exported `IDLE_INJECT` namespace.

## Integration Points
Clients from thermal/powercap code can register CPU masks, update duty cycles dynamically, and start/stop injection. The Kconfig option is `IDLE_INJECT`, and symbols are exported in namespace `"IDLE_INJECT"`.

## Risks
The framework relies on callers to provide higher-level synchronization against concurrent start/stop/unregister and duration updates. `idle_inject_set_duration()` ignores attempts to set both run and idle to zero, so callers cannot clear the period through that API. `idle_inject_start()` can be called repeatedly without an explicit running flag, potentially restarting an already active hrtimer. Registration prevents overlapping CPU masks by checking per-CPU ownership, but there is no lock around concurrent registrations.

## Test Signals
Test register/unregister with overlapping masks, start without duration, 100 percent idle (`run_duration_us=0`), stop while CPUs are in `play_idle_precise()`, CPU hotplug during stop/start, update callback skip/reschedule behavior, repeated start calls, and exported namespace usage by clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/powercap/idle_inject.c -->
