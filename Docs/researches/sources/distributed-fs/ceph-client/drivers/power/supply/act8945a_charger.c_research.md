# sources/distributed-fs/ceph-client/drivers/power/supply/act8945a_charger.c

## Purpose
`act8945a_charger.c` is a power-supply driver for the Active-semi ACT8945A PMIC charger. It reports charger status, charge type, battery health, capacity level, maximum current, model, and manufacturer from PMIC registers and optional GPIOs, and updates supply type on IRQ-driven state changes.

## Important APIs, Types, And Functions
- `struct act8945a_charger` stores the `power_supply`, mutable descriptor, parent regmap, IRQ work, init gate, and optional `lbo`/`chglev` GPIOs.
- `act8945a_get_charger_state()`, `act8945a_get_charge_type()`, `act8945a_get_battery_health()`, `act8945a_get_capacity_level()`, and `act8945a_get_current_max()` decode PMIC status/config/state registers into power-supply properties.
- `act8945a_enable_interrupt()` enables charger, input, temperature, and timer interrupt outputs and clears/arms status bits.
- `act8945a_set_supply_type()` mutates `desc.type` between mains, USB, and battery based on input-present and ACIN state.
- `act8945a_status_changed()` schedules work after initialization; `act8945a_work()` refreshes supply type and calls `power_supply_changed()`.
- `act8945a_charger_config()` reads DT properties, claims GPIOs, requests the LBO GPIO IRQ, and programs charger OVP/precondition/total timeout bits.

## Control Flow
Probe gets the parent regmap, configures charger registers from OF properties, obtains the main PMIC IRQ, initializes the descriptor and current supply type, registers the power supply, requests the PMIC IRQ, initializes work, enables charger interrupts, and sets `init_done`. IRQs from the PMIC and optional low-battery GPIO schedule work that refreshes descriptor type and notifies userspace.

Property reads synchronously read ACT8945A registers and optional GPIO levels. Charge state bits select charging, full, not charging, discharging, charge type, and current limit. Health distinguishes suspended charging, input present with temp/timer/overvoltage fault, and good states.

## State And Persistence
Driver state is minimal: `init_done`, mutable `desc.type`, GPIO descriptors, and pending work. Hardware configuration is persisted in ACT8945A registers until reset: OVP threshold, precondition timeout, total timeout, suspended-charging preservation, and interrupt enables. No software persistence exists.

## Dependencies And Integration Points
The driver depends on a parent regmap for ACT8945A registers, OF properties (`active-semi,input-voltage-threshold-microvolt`, `active-semi,precondition-timeout`, `active-semi,total-timeout`), optional GPIOs (`active-semi,lbo`, `active-semi,chglev`), `of_irq_get()`, and the power-supply framework.

## Risks
- `devm_gpiod_get_optional()` may return `NULL`, but the code calls `gpiod_to_irq(charger->lbo_gpio)` and `gpiod_get_value()` paths without explicit NULL handling for optional GPIO absence.
- The descriptor `type` is mutated at runtime. Consumers that cache type may not observe changes as expected, and tests should confirm power-supply core behavior.
- `act8945a_set_supply_type()` is declared `unsigned int` but returns negative regmap errors; this type mismatch can obscure failures.
- Health decoding collapses several disabled/input-present states into overheat, safety timer, or overvoltage based on status bits; incorrect PMIC bit interpretation would mislead charging policy.
- LBO IRQ request failures are logged as info and ignored, reducing notification quality without failing probe.

## Test Signals
- Regmap tests for each charger state: disabled, EOC with/without CHGDAT, fast, precharge, input present/absent, temp fault, timer fault, and suspended charging.
- GPIO tests for LBO and CHGLEV combinations in capacity-level and current-max calculations.
- Probe tests for DT defaults and all supported OVP/precondition/total-timeout values.
- IRQ tests should verify no notifications before `init_done`, work scheduling after PMIC/LBO IRQs, and clean `cancel_work_sync()` on remove.
