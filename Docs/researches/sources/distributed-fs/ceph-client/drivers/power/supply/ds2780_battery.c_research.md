# sources/distributed-fs/ceph-client/drivers/power/supply/ds2780_battery.c

Purpose: exposes Maxim/Dallas DS2780 1-Wire fuel-gauge data through a platform battery driver, with sysfs controls for PMOD, sense resistor, RSGAIN, PIO, and user/parameter EEPROM blocks.

Important APIs/types/functions: `struct ds2780_device_info` links the platform power supply to the parent 1-Wire device. `ds2780_battery_io()` delegates to the W1 DS2780 slave helper. Measurement helpers convert voltage, temperature, current/current-average, accumulated charge, relative capacity, status, and remaining active absolute charge. EEPROM helpers store and recall after writes.

Control flow: probe constructs a battery descriptor named from the platform device, attaches the DS2780 sysfs attribute group, and registers the supply. Property reads synchronously access 1-Wire registers and convert units. Sysfs stores validate simple ranges, write control/calibration registers, and persist register or EEPROM block changes where appropriate.

State and persistence: almost no measurement state is cached; reads go to the device. PMOD, sense resistor conductance, RSGAIN, and EEPROM bin writes persist to DS2780 EEPROM. PIO writes alter the special-feature register but are not copied to EEPROM in this path.

Dependencies and integration: depends on platform devices created by the W1 DS2780 slave layer, `w1_ds2780_io()`, `w1_ds2780_eeprom_cmd()`, DS2780 register definitions, power-supply core, and sysfs/bin attribute plumbing.

Risks and test signals: sense resistor zero is rejected, but integer division in current/charge scaling loses precision. This source snapshot includes an extra brace near `ds2780_get_control_register()`, so compile tests are required. Functional tests should cover all property reads, EEPROM bin offset/count behavior, PMOD/RSGAIN validation, sense resistor persistence, PIO writes, and 1-Wire error propagation.
