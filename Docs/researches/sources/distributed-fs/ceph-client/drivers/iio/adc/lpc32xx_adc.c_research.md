# sources/distributed-fs/ceph-client/drivers/iio/adc/lpc32xx_adc.c

## Purpose
`lpc32xx_adc.c` is a direct-mode IIO driver for the NXP LPC32xx 3-channel 10-bit ADC. It uses IRQ completion for conversions and optionally exposes scale when a `vref` regulator is available.

## Important APIs, types, and functions
- `struct lpc32xx_adc_state` stores MMIO base, clock, completion, optional vref regulator, mutex, and last value.
- `lpc32xx_read_raw()` enables the clock for each raw read, configures channel/reference selection, starts conversion, waits for ISR completion, disables the clock, and returns the cached value.
- `lpc32xx_adc_isr()` reads and masks the value register and completes the wait.
- Two channel tables exist: one with raw only and one with shared scale.

## Control flow
Probe maps MMIO, gets clock, requests IRQ, tries to get `vref`, selects the channel table based on regulator availability, initializes completion and mutex, and registers IIO. Raw conversion blocks indefinitely on `wait_for_completion()` until the IRQ fires.

## State and persistence
State is volatile: completion state, last ADC value, optional regulator pointer, and clock enablement during reads. Hardware selection and control registers are programmed per conversion. No persistent configuration exists.

## Dependencies and integration points
It uses platform/OF `nxp,lpc3220-adc`, MMIO, IRQs, completions, common clocks, optional regulator scaling, and IIO direct mode.

## Risks
- Raw reads have no timeout, so a missing IRQ can hang a userspace read.
- Missing `vref` silently removes scale ABI, which is deliberate but visible to consumers.
- The regulator is not enabled before reading voltage for scale; this relies on regulator framework behavior or an always-on reference.

## Test signals
Validate IRQ delivery, no-vref channel table, scale table with vref, channel selection constants, clock enable/disable per read, and behavior when conversion IRQ is lost.
