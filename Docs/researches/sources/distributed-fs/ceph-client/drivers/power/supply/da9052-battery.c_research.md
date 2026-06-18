# sources/distributed-fs/ceph-client/drivers/power/supply/da9052-battery.c

Purpose: exposes Dialog DA9052 PMIC battery state using PMIC status registers, charger-end/current registers, ADC voltage/temperature readings, and fixed voltage-capacity lookup tables.

Important APIs/types/functions: `struct da9052_battery` holds PMIC pointer, power supply, USB current notifier, charger type, status, and health. `da9052_bat_check_status()` interprets DCIN/VBUS selection/detect and charge-end flags. `da9052_bat_read_capacity()` interpolates capacity from voltage and temperature lookup tables. `da9052_bat_irq()` handles PMIC IRQs; `da9052_USB_current_notifier()` updates USB current limit.

Control flow: probe allocates state, initializes defaults, applies platform `use_for_apm`, requests TBAT/DCIN/VBUS/CHGEND IRQs, and registers `da9052-bat`. Property reads check battery presence via temperature threshold, reject most properties when battery is illegal, then read or derive status, online, health, voltage, current, capacity, temperature, and technology. IRQs update status/full state and notify the supply.

State and persistence: status, charger type, and health are cached in memory and refreshed on reads/IRQs. The USB current notifier writes DA9052 current-limit registers, so current-limit changes persist in PMIC state until changed/reset. Capacity is derived each read rather than stored.

Dependencies and integration: depends on DA9052 MFD core, regmap IRQ virqs, PMIC ADC helpers, platform data, and power-supply registration.

Risks and test signals: this tree has duplicated `da9052_reg_read()` in the USB current notifier and a temperature table index branch that appears logically unreachable/reversed for some ranges. Test IRQ request/free unwind, battery absent/illegal path, DCIN/VBUS priority, charge-end current comparison, capacity interpolation at table boundaries, USB current-limit validation, and unit consistency for voltage/current/temp properties.
