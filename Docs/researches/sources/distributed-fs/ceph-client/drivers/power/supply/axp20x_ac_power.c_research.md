<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/axp20x_ac_power.c -->
# sources/distributed-fs/ceph-client/drivers/power/supply/axp20x_ac_power.c

## Purpose

`axp20x_ac_power.c` registers the ACIN mains power-supply interface for X-Powers AXP20x, AXP22x, and AXP813 PMIC variants. It exposes AC adapter presence, online state, health, and, on ADC-capable AXP20x variants, instantaneous ACIN voltage/current through the Linux power-supply class. AXP813 has a different feature set: it does not expose ACIN ADC channels here, but it exposes writable ACIN path enable, hold voltage, and input-current limit controls.

## Important APIs, Types, And Functions

The central runtime object is `struct axp20x_ac_power`, which stores the parent regmap, registered `power_supply`, optional IIO ACIN voltage/current channels, the AXP813 path-select capability flag, and a flexible IRQ array. `struct axp_data` provides variant data: the `power_supply_desc`, IRQ names, whether ACIN ADC channels are required, and whether `AXP813_ACIN_PATH_CTRL` path selection applies.

`axp20x_ac_power_get_property()` implements `HEALTH`, `PRESENT`, `ONLINE`, `VOLTAGE_NOW`, `CURRENT_NOW`, `VOLTAGE_MIN`, and `INPUT_CURRENT_LIMIT` depending on the active descriptor. It reads `AXP20X_PWR_INPUT_STATUS` for ACIN present/available bits, uses IIO for ADC-backed properties, and decodes AXP813 `VHOLD` and current-limit fields. `axp813_ac_power_set_property()` writes AXP813 `ONLINE`, `VOLTAGE_MIN`, and `INPUT_CURRENT_LIMIT` after range checks. `axp20x_ac_power_irq()` only calls `power_supply_changed()`.

## Control Flow

Probe rejects disabled device-tree nodes, obtains the parent `axp20x_dev`, selects variant data from the OF match, allocates state sized for the IRQ count, optionally gets `acin_v` and `acin_i` IIO channels, registers the power supply, then maps named platform IRQs through the parent regmap IRQ controller and requests them. IRQs are requested after registration because they may fire immediately.

Suspend/resume treats the first IRQ, `ACIN_PLUGIN`, as the wake source when the power-supply device may wake the system. Remaining nested threaded IRQs are explicitly disabled during suspend and re-enabled on resume.

## State And Persistence

The driver keeps minimal cached software state: pointers, capability flags, and virtual IRQ numbers. User-visible values are read live from PMIC registers or IIO channels. AXP813 writes persist in PMIC hardware registers until firmware, another driver, or reset changes them. There is no nonvolatile storage or delayed work.

## Dependencies And Integration Points

The driver depends on the AXP20x MFD parent for regmap and regmap IRQ data, OF compatible strings, IIO channels named `acin_v`/`acin_i` for AXP20x, and the power-supply framework. It integrates via compatibles `x-powers,axp202-ac-power-supply`, `x-powers,axp221-ac-power-supply`, and `x-powers,axp813-ac-power-supply`.

## Risks And Edge Cases

AXP813 field conversion is step-based and truncates unsupported values; callers must use exact supported ranges. `ONLINE` is filtered by ACIN path-select on AXP813, so ACIN can be electrically available while reported offline. IIO channel absence returns probe deferral only for `-ENODEV`; other IIO errors abort probe. Suspend assumes IRQ ordering matches the `axp20x_irq_names[]` array, with plugin first.

## Test Signals

Compile with AXP20x MFD, power-supply, IIO, and PM sleep enabled. Runtime tests should verify AC plug/removal interrupts, ACIN voltage/current scaling on AXP20x, AXP813 writable `online`, `voltage_min`, and `input_current_limit`, and wake-from-suspend only on ACIN insertion. Fault injection should cover regmap read failures and missing IIO channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/power/supply/axp20x_ac_power.c -->
