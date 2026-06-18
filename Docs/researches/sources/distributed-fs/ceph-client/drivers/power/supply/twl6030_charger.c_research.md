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
