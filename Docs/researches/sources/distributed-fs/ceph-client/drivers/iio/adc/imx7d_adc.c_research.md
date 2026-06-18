# sources/distributed-fs/ceph-client/drivers/iio/adc/imx7d_adc.c

## Purpose
`imx7d_adc.c` is a direct-mode IIO ADC driver for the Freescale/NXP i.MX7D ADC. It exposes sixteen logical voltage channels, using four hardware conversion channels with interrupt-driven completion.

## Important APIs, types, and functions
- `struct imx7d_adc` holds MMIO, ADC clock, vref regulator, completion, mutex, current channel, last value, predivider, and feature configuration.
- `struct imx7d_adc_feature` stores predivider, averaging count, and core time unit.
- `imx7d_adc_hw_init()` powers up the ADC, enables channel interrupts, and programs sample rate.
- `imx7d_adc_channel_set()` configures the selected hardware channel for single conversion with averaging.
- `imx7d_adc_read_data()` extracts 12-bit results from shared A/B or C/D result registers.
- `imx7d_adc_isr()` completes reads and clears conversion or timeout status bits.

## Control flow
Probe maps registers, gets IRQ, clock, and `vref`, registers cleanup through `devm_add_action_or_reset`, initializes feature defaults, enables regulator and clock, programs hardware, requests the IRQ, and registers IIO. A raw read masks the requested logical channel to one of four hardware channels, configures it, waits up to 100 ms for completion, and returns the captured value.

## State and persistence
The driver stores sample-rate configuration and current channel in memory and programs ADC power, timing, averaging, and channel config registers. Runtime suspend powers the ADC down and disables clock/regulator; resume reverses this. No user-written persistent configuration is exposed.

## Dependencies and integration points
It uses platform/OF `fsl,imx7d-adc`, MMIO, IRQs, completions, common clocks, regulators, IIO direct mode, and simple device PM ops.

## Risks
- Only `chan->channel & 0x03` selects hardware channels, so the sixteen exposed logical channels map onto four hardware result lanes.
- Interrupt status clearing writes a modified status value; changes to write-one-to-clear semantics would be dangerous.
- Sample-rate values are fixed by feature defaults; no runtime setter is exposed.

## Test signals
Read all exposed channels, verify mapping to hardware inputs, check scale from `vref`, inspect sample frequency, exercise suspend/resume, and simulate conversion timeout status bits to confirm logging and clearing.
