# sources/distributed-fs/ceph-client/drivers/iio/adc/lpc18xx_adc.c

## Purpose
`lpc18xx_adc.c` is a simple direct-mode IIO driver for the NXP LPC18xx ADC. It supports eight 10-bit voltage channels through polling and explicitly does not support hardware triggers, burst mode, interrupts, or DMA.

## Important APIs, types, and functions
- `struct lpc18xx_adc` stores vref regulator, MMIO base, device, mutex, clock, and cached control-register value.
- `lpc18xx_adc_read_chan()` writes control bits for one channel and start-now, then polls the global data register for conversion done.
- `lpc18xx_adc_read_raw()` handles raw and scale attributes.
- Probe computes ADC clock divider against a 4.5 MHz target, powers the ADC with `PDN`, registers cleanup actions, and registers IIO.

## Control flow
Probe maps MMIO, gets an already-enabled clock, gets and enables `vref`, computes `cr_reg`, writes it to the control register, and registers a direct-mode IIO device. A raw read takes the mutex, writes the selected channel and start bit, polls for done with microsecond timeout, extracts the 10-bit sample, and returns it.

## State and persistence
The driver caches only the base control register. Hardware control register state is cleared through a devm cleanup action on detach. No user settings persist.

## Dependencies and integration points
It uses platform/OF `nxp,lpc1850-adc`, MMIO, common clocks, regulators, IIO direct mode, and `readl_poll_timeout()`.

## Risks
- Poll timeout is very short; slow clocks or wrong divider can cause read failures.
- Scale assumes `regulator_get_voltage()` succeeds; a negative value would be divided and returned as scale.
- Clock divider calculation uses `DIV_ROUND_UP(rate, target)` directly in the register field; hardware off-by-one expectations must match the manual.

## Test signals
Probe with representative clock rates, read all eight channels, verify poll timeout behavior, validate scale from vref, and confirm cleanup clears the control register.
