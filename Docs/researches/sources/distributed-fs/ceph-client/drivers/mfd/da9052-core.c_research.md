# sources/distributed-fs/ceph-client/drivers/mfd/da9052-core.c

## Purpose
`da9052-core.c` is the common MFD core for Dialog DA9052/DA9053 PMICs. It defines the regmap access policy, ADC helpers, fault-log handling, and the child device set shared by the I2C and SPI bus front-ends.

## Important APIs, Types, and Functions
The exported `da9052_regmap_config` constrains readable, writeable, and volatile registers with `da9052_reg_readable()`, `da9052_reg_writeable()`, and `da9052_reg_volatile()`. Exported helpers `da9052_adc_manual_read()` and `da9052_adc_read_temp()` provide manual ADC conversions and battery-temperature lookup. `da9052_device_init()` and `da9052_device_exit()` are called by bus drivers. `da9052_clear_fault_log()` records and clears reset/fault causes. `da9052_subdev_info` and `da9052_tsi_subdev_info` enumerate regulator, onkey, RTC, GPIO, hwmon, LED, battery, watchdog, and optional touchscreen children.

## Control Flow
The bus driver allocates `struct da9052`, initializes the regmap, and calls `da9052_device_init()`. Core init creates the ADC mutex/completion, clears the fault log, calls optional platform init, sets the chip id, initializes the regmap IRQ chip through `da9052_irq_init()`, registers common MFD children, and conditionally registers the TSI child unless `dlg,tsi-as-adc` is present. Manual ADC reads serialize on `auxadc_lock`, program `DA9052_ADC_MAN_REG`, wait up to 500 ms for the ADC completion, and combine high/low result registers.

## State and Persistence
Runtime state lives in `struct da9052`: regmap, chip id, IRQ data, fault log, ADC mutex, and ADC completion. Hardware state is the PMIC register file, including volatile status/event/ADC/RTC fields. The driver does not persist state across reboot; it only captures the current fault log in memory before clearing it in hardware.

## Dependencies and Integration Points
The file depends on Linux regmap, MFD core, property APIs, DA9052 register definitions, and `da9052_irq_init()` from the IRQ companion file. Child drivers consume named MFD devices and internal IRQ resources. `device_property_read_bool()` allows device tree or ACPI-style firmware to alter TSI registration.

## Risks and Edge Cases
`da9052_device_init()` clears the fault log before `chip_id` is assigned, while bus-specific I/O errata handling may depend on `chip_id`; platforms relying on the I2C parking fix during the earliest reads need careful validation. ADC reads fail on invalid channel, IRQ timeout, or register I/O error. The TBAT lookup assumes an 8-bit result and treats zero or negative register returns as errors. If TSI pins are physically used as ADC inputs but `dlg,tsi-as-adc` is omitted, an unwanted touchscreen child is created.

## Test Signals
Useful signals include regmap access-table acceptance of expected PMIC registers, fault-log read/clear logs, successful child registration, ADC conversion interrupt completion, timeout behavior with the ADC IRQ masked, TBAT lookup values, and `dlg,tsi-as-adc` toggling TSI child creation.
