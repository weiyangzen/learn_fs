<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/units.h -->
# sources/distributed-fs/ceph-client/include/linux/units.h

Purpose: centralizes common unit scale constants and temperature conversion helpers for kernel drivers and subsystems.

Important APIs and types: metric scale macros cover `PETA` through `FEMTO` as integer multipliers/divisors by convention. Ratio scales include `PERCENT`, `PERMILLE`, `PERMYRIAD`, and `PERCENTMILLE`. Frequency, power, energy, and bit/byte conversion constants include `NANOHZ_PER_HZ`, `HZ_PER_MHZ`, `MICROWATT_PER_WATT`, and `BYTES_PER_GBIT`. Temperature helpers convert among milliKelvin, milliCelsius, Kelvin, Celsius, and deciKelvin, using `ABSOLUTE_ZERO_MILLICELSIUS` and rounded division.

Control flow: consumers include this header and use named constants or inline conversions rather than open-coded scaling. Temperature conversions add or subtract absolute-zero offset and round when reducing precision.

State and persistence: no state is stored. Results are pure arithmetic values used by sensors, thermal, power, clock, and hardware-monitoring paths.

Dependencies and integration points: depends on `bits.h` for `BITS_PER_BYTE` and `math.h` for `DIV_ROUND_CLOSEST`. It integrates with drivers that exchange values in hardware-specific units and kernel/user-visible standard units.

Risks and test signals: risks include overflow when multiplying before conversion, confusion between numerator-style macros such as `MILLI` and SI fractional meanings, negative temperature rounding surprises, and unit mismatch in ABI attributes. Test boundary temperatures, large frequency/power values, byte/bit conversions, and hardware-monitoring sysfs expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/units.h -->
