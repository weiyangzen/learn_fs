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
