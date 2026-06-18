# sources/distributed-fs/ceph-client/drivers/regulator/da9055-regulator.c

## Purpose
This file provides DA9055 PMIC buck and LDO regulators. It supports voltage register set A/B selection, suspend voltage programming, regulator mode control, buck current limits, optional GPIO-controlled enable/register selection, and over-current notification for LDO5/LDO6.

## Important APIs, Types, And Functions
Descriptor metadata is split across `struct da9055_conf_reg`, `struct da9055_volt_reg`, `struct da9055_mode_reg`, and `struct da9055_regulator_info`. Runtime state in `struct da9055_regulator` includes the parent DA9055 pointer, selected descriptor, registered `rdev`, and register-select GPIO mode.

Key operations are `da9055_buck_get_mode()`, `da9055_buck_set_mode()`, `da9055_ldo_get_mode()`, `da9055_ldo_set_mode()`, `da9055_regulator_get_voltage_sel()`, `da9055_regulator_set_voltage_sel()`, `da9055_regulator_set_suspend_voltage()`, `da9055_suspend_enable()`, `da9055_suspend_disable()`, `da9055_gpio_init()`, and `da9055_ldo5_6_oc_irq()`.

## Control Flow
The platform driver registers at `subsys_initcall()`. Probe selects descriptor info by `pdev->id`, binds parent DA9055/regmap/platform data into `regulator_config`, initializes optional GPIO control, registers the regulator, and for LDO5/LDO6 requests the named `REGULATOR` IRQ to emit `REGULATOR_EVENT_OVER_CURRENT`.

Voltage reads first inspect the active A/B register select bit, then read the corresponding voltage register. Voltage writes select register set A and update A when no external register-select GPIO is configured; if a GPIO selects A/B, the driver reads the active selection and writes the matching register. Suspend voltage is mapped linearly and written to register set B, with software selecting B when no GPIO handles selection. Suspend enable/disable switch between B and A in the same no-GPIO case.

## State And Persistence
Static descriptor data covers BUCK1, BUCK2, and LDO1-LDO6. Runtime state tracks whether register selection is software controlled or external GPIO controlled. Hardware state is in DA9055 PMIC registers, including mode fields, voltage A/B registers, enable bits, and current-limit selector bits.

## Dependencies And Integration Points
It depends on the DA9055 MFD core/register definitions, regmap, optional platform data arrays for regulator init and GPIO mux selections, GPIO descriptors named `regulator-enable`, `enable`, and `regulator-select`, regulator core regmap helpers, and threaded IRQ delivery for over-current events.

## Risks
`da9055_gpio_init()` dereferences `pdata` for GPIO mux arrays when optional GPIOs are present, so DT/platform configurations with GPIO properties but no platform data can fail badly. Mode setters default `val = 0` and do not reject unsupported mode values, which can silently program an unintended mode. Register-set A/B behavior is sensitive to GPIO mux configuration. LDO5/LDO6 IRQ request tolerates `-EBUSY`, so shared interrupt behavior should be verified.

## Test Signals
Validate probe for every ID, GPIO and non-GPIO A/B selection paths, normal and suspend voltage writes, mode get/set for bucks and LDOs, buck current limit selector fields, enable/disable regmap behavior, LDO5/LDO6 over-current notifier delivery, and error handling for missing platform data or IRQ resources.
