# sources/distributed-fs/ceph-client/drivers/power/supply/ds2781_battery.c

Purpose: provides the Maxim/Dallas DS2781 1-Wire fuel-gauge power-supply driver. It mirrors the DS2780-style interface while using DS2781 register definitions and status logic that consults whether the battery is externally supplied.

Important APIs/types/functions: `struct ds2781_device_info` stores device pointers and battery descriptor. `ds2781_battery_io()` delegates to W1 DS2781 helpers. `ds2781_get_voltage()`, `ds2781_get_temperature()`, `ds2781_get_current()`, `ds2781_get_accumulated_current()`, `ds2781_get_capacity()`, and `ds2781_get_status()` implement property reads. Sysfs attributes manage PMOD, sense resistor, RSGAIN, PIO, and EEPROM blocks.

Control flow: probe creates a battery descriptor with the DS2781 property set and sysfs group, then registers the power supply. Each property read performs W1 register access and conversion. Status reads capacity/current and uses `power_supply_am_i_supplied()` to distinguish charging/not-charging/full from discharging. Sysfs writes update registers and persist calibration/control values through DS2781 EEPROM copy/recall commands.

State and persistence: measurement data is not cached in driver state. PMOD, sense resistor conductance, RSGAIN, and bin EEPROM writes persist in the gauge. PIO writes affect the special-feature register. The external supply relationship affects reported status but is not stored.

Dependencies and integration: depends on W1 DS2781 slave helpers and register definitions, platform-device binding, sysfs/bin attributes, and the power-supply core including external supply detection.

Risks and test signals: this snapshot contains a doubled opening brace in `ds2781_get_control_register()` and an extra closing brace at file end, so compile testing is mandatory. Test negative/sign extension in voltage/temp/current conversions, EEPROM store/recall failures, sense resistor zero, status transitions with/without external power, sysfs validation, and bin attribute read/write offsets.
