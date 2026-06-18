# sources/distributed-fs/ceph-client/drivers/regulator/max77857-regulator.c

Purpose: supports ADI/MAX77831, MAX77857, MAX77859, and MAX77859A buck-boost converters with variant-specific voltage encoding, mode control, ramp rates, status/error reporting, and optional MAX77859A current limits.

Important APIs/types/functions: `max77857_get_status()`, `max77857_get_mode()`, `max77857_set_mode()`, and `max77857_get_error_flags()` expose POK, FPWM, and fault bits. MAX77859 voltage setters use 16-bit bulk register access plus a DVS-start bit. `max77857_calc_range()` adjusts linear voltage ranges from feedback resistor properties.

Control flow: probe determines variant from I2C ID, stores it in device driver data for regmap volatile decisions, mutates the global descriptor for MAX77859/MAX77859A, adjusts ranges from DT, initializes regmap, optionally programs switch frequency and ramp table, parses regulator init data, and registers one regulator.

State and persistence: file-scope descriptor and linear-range arrays are mutated at probe time, while regmap cache uses volatile interrupt-source registers. Hardware stores voltage/mode/current settings.

Dependencies and integration: depends on I2C, regmap maple cache, OF properties `adi,rtop-ohms`, `adi,rbot-ohms`, `adi,switch-frequency-hz`, and regulator status/error APIs.

Risks and test signals: global descriptor mutation is unsafe for multiple simultaneous variants. `get_status()` and error flags read the MAX77857 interrupt register even for MAX77859 variants. Test mixed-device probes, big-endian voltage writes, current-limit clamping, switch-frequency selection, and resistor-derived range math.
