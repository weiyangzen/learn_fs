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
