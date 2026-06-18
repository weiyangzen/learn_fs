# sources/distributed-fs/ceph-client/drivers/rtc/rtc-max31335.c

Purpose: supports Analog Devices/Maxim MAX31331 and MAX31335 I2C RTCs with time, alarm, optional IRQs, SRAM NVMEM, configurable trickle charger, optional clock output, and MAX31335 temperature hwmon.

Important APIs and types: `struct chip_desc` abstracts register locations and capabilities per chip; `struct max31335_data` stores regmap, RTC, clock output, input clock, chip descriptor, and IRQ. RTC callbacks are `max31335_read_time()`, `max31335_set_time()`, `max31335_read_alarm()`, `max31335_set_alarm()`, and `max31335_alarm_irq_enable()`. Extra integration is handled by `max31335_clkout_register()`, `max31335_nvmem_reg_read/write()`, `max31335_read_temp()`, and `max31335_trickle_charger_setup()`.

Control flow: probe initializes an I2C regmap, selects chip data, allocates the RTC with range 2000-2199 and one-day alarm offset max, registers/disables clkout based on `#clock-cells`, requests threaded alarm IRQ if present, clears alarm feature if not, registers NVMEM, optionally registers hwmon for temperature, configures trickle charging from firmware properties, then registers the RTC. Time and alarm operations bulk-read/write BCD fields and manipulate the A1 interrupt/status bits. IRQ handling locks the RTC ops mutex, clears A1F, and emits `RTC_AF`.

State and persistence: date/time, alarm, interrupt flags, SRAM, trickle-charger setting, clock-output register, and temperature data are chip registers. Software state only tracks descriptor and registrations.

Dependencies and integration: I2C, regmap with volatile register callback, RTC class, optional common clock provider, `devm_rtc_nvmem_register()`, optional hwmon, firmware properties `aux-voltage-chargeable`, `trickle-resistor-ohms`, `adi,tc-diode`, and OF/I2C match tables.

Risks: `MAX31335_YEAR` is defined with the same value as month, though code uses descriptor offsets for time. `max31335_alarm_irq_enable()` passes `enabled` directly as bit value instead of using `FIELD_PREP`, relying on bit zero semantics for A1IE. The global static NVMEM config is mutated per probe, which is fragile for multiple devices. Trickle setup silently ignores unsupported resistor values.

Test signals: MAX31331 versus MAX31335 descriptor paths, 2099/2100 century bit behavior, alarm IRQ clear and pending state, no-IRQ alarm feature clearing, NVMEM read/write offsets, clkout rates/enabling/no provider path, hwmon temperature conversion, and all trickle property combinations.
