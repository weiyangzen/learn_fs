# sources/distributed-fs/ceph-client/drivers/iio/adc/ep93xx_adc.c

## Purpose
`ep93xx_adc.c` is a direct-mode IIO voltage ADC driver for the Cirrus Logic EP93xx SoC ADC block. It exposes eight single-ended voltage channels with raw, scale, and offset attributes and deliberately polls conversion completion because reading the result register starts conversion and the hardware conversion-rate spacing makes IRQ mode impractical.

## Important APIs, types, and functions
- `struct ep93xx_adc_priv` stores the ADC clock, MMIO base, last selected channel, and a mutex that serializes channel switching and conversion.
- `ep93xx_adc_channels` defines the eight IIO voltage channels, including datasheet names for the touchscreen-style pins.
- `ep93xx_read_raw()` implements `IIO_CHAN_INFO_RAW`, `IIO_CHAN_INFO_OFFSET`, and `IIO_CHAN_INFO_SCALE`.
- `ep93xx_adc_probe()` allocates the IIO device, maps MMIO, gets and enables the clock, optionally programs the ADC clock from the parent, and registers the device.
- `ep93xx_adc_remove()` unregisters IIO and disables the clock.

## Control flow
Probe initializes `lastch` to `-1`, sets `INDIO_DIRECT_MODE`, assigns the fixed channel table, and enables the hardware clock. A raw read takes the mutex, switches channels only if needed, performs the software-lock write sequence with local IRQs disabled, waits for settling, triggers a conversion by reading `EP93XX_ADC_RESULT`, delays to stay under the maximum conversion rate, and then polls for `EP93XX_ADC_SDR` until a short timeout.

## State and persistence
The driver has no persistent storage. Runtime state is the selected channel cached in `lastch` and the clock/MMIO handles. Hardware state includes the switch register and ADC conversion engine. Scale and offset are fixed constants based on the expected 3.3 V supply and documented input range.

## Dependencies and integration points
This file integrates with the platform bus, device tree match `cirrus,ep9301-adc`, IIO direct mode, MMIO register access, the common clock framework, and high-resolution timer availability for conversion delays.

## Risks
- Channel switch unlock and write must be adjacent; interrupt masking is intentional.
- Without high-resolution timers the busy-wait delay path can consume a full CPU during back-to-back reads.
- The scale assumes a typical 3.3 V supply, not a regulator-measured reference.
- Timeout handling depends on jiffies after a fixed conversion delay, so timing regressions can be hardware-sensitive.

## Test signals
Build with the EP93xx ADC config, probe from DT, read all raw channels repeatedly, verify channel switching does not corrupt adjacent reads, and check scale/offset ABI values. Hardware tests should confirm maximum-rate reads do not trigger conversion timeouts.
