# sources/distributed-fs/ceph-client/drivers/hwmon/lan966x-hwmon.c

## Purpose
`lan966x-hwmon.c` is a platform hwmon driver for Microchip LAN966x hardware. It exposes one PVT temperature input, one fan tachometer input, and writable PWM duty/frequency controls.

## Important APIs, types, and functions
The driver uses platform resources by name, MMIO regmap, clocks, polynomial temperature conversion, OF matching, devm cleanup actions, and hwmon `with_info`. `struct lan966x_hwmon` stores PVT and fan regmaps plus the enabled clock and clock rate. `lan966x_hwmon_read_temp()` reads and converts the PVT ADC sample through `polynomial_calc()`. `lan966x_hwmon_read_fan()` converts fan pulses per second to RPM. PWM helpers read/write duty and frequency register fields.

## Control flow
Probe enables the clock, records its rate, maps named `pvt` and `fan` resources as regmaps, programs the PVT sensor into continuous sampling mode with a divider targeting about 1.2 MHz, installs a devm cleanup action to disable sampling, and registers the hwmon device. Runtime reads dispatch by hwmon type and attribute. PWM writes validate ranges, convert requested frequency to register units, clamp to the field width, and update regmap bits.

## State and persistence
The driver programs hardware sampling state and PWM registers. The sampling configuration is disabled automatically on device teardown through `devm_add_action_or_reset()`. No sensor-value cache is kept. PWM duty/frequency stay in hardware until rewritten or reset.

## Dependencies and integration points
It requires a device tree compatible `microchip,lan9668-hwmon`, a clock, and two named MMIO resources. It depends on `linux/polynomial.h` for integer conversion of raw PVT ADC counts to millidegrees Celsius.

## Risks
The PVT conversion is a fourth-order polynomial with redistributed integer factors; regression risk is high if term order or scaling is changed. The frequency formula intentionally differs from the datasheet by using `pwm_freq + 1`, so tests should preserve that behavior. Temperature reads can return `-ENODATA` until valid data is latched. Incorrect clock rate or resource names break all conversions.

## Test signals
Test OF probe with missing clock/resources, PVT enable/disable register writes, temperature valid and invalid status, polynomial conversion at raw endpoints, fan RPM conversion, PWM duty boundaries, PWM frequency conversion/clamping, and hwmon permissions for read-only vs writable attributes.
