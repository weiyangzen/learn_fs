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
