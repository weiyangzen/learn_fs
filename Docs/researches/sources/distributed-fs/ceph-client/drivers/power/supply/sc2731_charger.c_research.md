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
