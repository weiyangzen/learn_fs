# sources/distributed-fs/ceph-client/drivers/power/supply/ltc2941-battery-gauge.c

## Purpose
This I2C driver supports LTC2941/LTC2942/LTC2943/LTC2944 battery gas gauges. It exposes accumulated charge, charge thresholds, voltage, temperature, and current according to chip capabilities, periodically detects charge-register changes, and disables continuous ADC conversion during shutdown for ADC-capable chips.

## Important APIs, Types, and Functions
`struct ltc294x_info` stores the I2C client, power supply, descriptor, delayed work, chip ID, last charge register, sense resistor, and computed `Qlsb` conversion. `ltc294x_read_regs()` and `ltc294x_write_regs()` implement multi-byte I2C access. Conversion helpers translate between register counts and uAh, accounting for negative sense-resistor orientation. `ltc294x_reset()` sets prescaler, scan/monitor mode, and ALCC disabled. Getters decode charge thresholds/current charge/counter, voltage by chip family, current by sense resistor, and temperature. Setters write charge thresholds and safely update accumulated charge by shutting down the analog section temporarily.

## Control Flow
Probe reads OF match chip type and node name, requires `lltc,resistor-sense`, reads optional `lltc,prescaler-exponent`, computes `Qlsb`, distinguishes LTC2941 versus LTC2942 from status, trims property count by chip capability, registers autocancel delayed work, programs control mode, registers the battery supply, and starts 10-second polling. Suspend cancels delayed work; resume restarts it. Shutdown disables ADC scan for non-LTC2941 devices.

## State and Persistence
The driver caches conversion constants and last observed charge register. Charge thresholds and charge-now writes persist in gauge registers. Polling state is delayed work only; the hardware accumulator continues operating independently.

## Dependencies and Integration Points
It depends on I2C combined transfers and SMBus block writes, OF properties for sense resistor and prescaler, power-supply writable properties, PM sleep hooks, and device compatibles for each LTC294x variant.

## Risks
`ltc294x_get_voltage()` computes from `datar` even if the read failed before returning the error. `of_property_read_u32()` is used for a signed `s32 r_sense`, which makes negative sense orientation questionable through unsigned DT parsing. Current conversion divides by `r_sense`; a zero value is not explicitly rejected. The descriptor name comes from `np->name`, so missing OF would be unsafe in this implementation.

## Test Signals
Validate chip identification, property counts per chip, Qlsb conversion for prescaler and sense resistor values, negative-current orientation, charge threshold and charge-now writes, polling change events, suspend/resume, shutdown ADC disable, and failed I2C read/write propagation.
