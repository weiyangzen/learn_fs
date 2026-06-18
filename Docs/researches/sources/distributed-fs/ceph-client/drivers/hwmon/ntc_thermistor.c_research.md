# sources/distributed-fs/ceph-client/drivers/hwmon/ntc_thermistor.c

Purpose: generic platform hwmon driver for NTC thermistors connected through an IIO voltage ADC and a configured resistor divider. It converts ADC voltage to thermistor resistance and then to temperature using built-in compensation tables.

Important APIs/types/functions: `struct ntc_compensation` and `struct ntc_type` model sorted resistance/temperature tables. `struct ntc_data` stores electrical parameters, connection orientation, IIO channel, and table selection. Core functions are `ntc_adc_iio_read()`, `get_ohm_of_thermistor()`, `lookup_comp()`, `get_temp_mc()`, `ntc_read()`, `ntc_thermistor_parse_props()`, and probe.

Control flow: probe gets an IIO voltage channel, reads `pullup-uv`, `pullup-ohm`, `pulldown-ohm`, and `connected-positive`, validates the divider, selects a table from OF/platform match data, and registers hwmon. Reads fetch processed voltage, fall back through raw conversion and a 12-bit assumption if needed, compute resistance for positive or ground-connected divider topologies, reject out-of-range values, binary-search the descending table, and linearly interpolate millidegrees Celsius.

State and persistence: configuration is immutable after probe. No periodic cache is kept; every `temp1_input` read samples the IIO channel. The only persistent state is the selected table and electrical parameters.

Dependencies and integration: depends on IIO consumer APIs, firmware properties, fixed-point interpolation, and hwmon chip info. Compatible strings cover EPCOS, Murata, Samsung, and deprecated `ntc,*` aliases.

Risks: fallback raw conversion assumes a 12-bit ADC and Vref equal to pullup voltage. Divider equations can saturate to `UINT_MAX` for zero divisors. Compensation tables must remain sorted by descending resistance. A zero or rail ADC reading is treated as no data.

Test signals: property validation failures, ADC processed/raw fallback paths, both connection orientations, interpolation at table points and between points, out-of-range resistance rejection, and `temp1_type` reporting thermistor type 4.
