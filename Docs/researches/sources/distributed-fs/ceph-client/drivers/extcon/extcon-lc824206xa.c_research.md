# sources/distributed-fs/ceph-client/drivers/extcon/extcon-lc824206xa.c

## Purpose
`extcon-lc824206xa.c` supports the ON Semiconductor LC824206XA microUSB switch/accessory detector. It reports USB host and charger types, controls a VBUS boost regulator, switches DP/DM routing, and exposes charger-detection data as a power-supply.

## Important APIs, types, and functions
`struct lc824206xa_data` stores work, I2C client, extcon, power-supply, VBUS regulator, cable/USB type, switch state, VBUS state, and a fast-charge quirk. Main helpers are `lc824206xa_work()`, `lc824206xa_charger_detect()`, `lc824206xa_get_id()`, `lc824206xa_set_vbus_boost()`, `lc824206xa_irq()`, and `lc824206xa_psy_get_prop()`.

## Control flow
Probe initializes undocumented chip registers, clears/masks interrupts, enables automatic ID ADC and charger detection, registers extcon and power-supply devices, requests a low-level threaded IRQ, and schedules initial work. IRQ handling reads/clears interrupt status and schedules work. Work reads status, computes valid VBUS vs OVP, optionally performs continuous ID ADC conversion, handles GND/ACA/float ID states, detects charger type for floating ID with VBUS, controls VBUS boost and switch routing, updates extcon cable state, and notifies the power-supply.

## State and persistence behavior
Runtime state includes current/previous cable, current/previous switch-control value, USB type, VBUS validity, and boost state. Register programming persists only while hardware remains powered.

## Dependencies and integration points
It depends on I2C SMBus byte access, extcon, regulator, power_supply, IRQs, workqueues, and an optional `onnn,enable-miclr-for-dcp` device property.

## Risks and edge cases
Register meanings are reverse-engineered from Android sources, so bit semantics may be incomplete. ID values during slow insertion can be transient and are partly handled with debug logs. Fast-charge-over-mic-L/R uses OVP as part of state recognition. IRQ clear requires writing bits then zero, so missed ordering can leave the line asserted. Work is not devm-autocancelled explicitly.

## Test signals
Test GND host, ACA, float no-VBUS, SDP/CDP/DCP/QC, OVP fast-charge quirk, VBUS boost regulator transitions, switch-control writes, power-supply current/USB type properties, IRQ clear behavior, and I2C error paths.
