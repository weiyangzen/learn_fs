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
