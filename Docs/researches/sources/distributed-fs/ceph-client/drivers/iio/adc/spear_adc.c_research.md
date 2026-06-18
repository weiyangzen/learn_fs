# sources/distributed-fs/ceph-client/drivers/iio/adc/spear_adc.c

## Purpose
This platform IIO driver supports the ST SPEAr ADC, primarily `st,spear600-adc`, with eight voltage channels, direct raw reads, scale reporting, and configurable sampling frequency.

## Important APIs, types, and functions
`struct spear_adc_state` stores register layout pointers for SPEAr3xx and SPEAr6xx views, clock, completion, mutex, current clock, sampling frequency, average sample count, VREF selection, and last value. Register abstraction helpers include `spear_adc_set_status()`, `spear_adc_set_clk()`, `spear_adc_set_scanrate()`, and `spear_adc_get_average()`. IIO operations are `spear_adc_read_raw()` and `spear_adc_write_raw()`.

## Control flow
Probe maps the register block, enables the clock, requests an IRQ, reads required `sampling-frequency` and optional `average-samples` and `vref-external` properties, resets/configures ADC registers, initializes completion, and registers IIO. A raw read locks the device, builds a status word containing channel, averaging, start, enable, and VREF selection, writes it, waits for ISR completion, returns the ISR-captured average value, and unlocks. Sampling-frequency writes validate the requested range and reprogram clock high/low counts.

## State and persistence
Sampling frequency and current derived ADC clock are cached in `sampling_freq` and `current_clk`. Average samples and external VREF are firmware-defined. Last conversion result is stored in `value` by the ISR. Hardware configuration is set at probe and adjusted only by sampling-frequency writes.

## Dependencies and integration points
It depends on platform MMIO, clock, IRQ, firmware properties, and IIO direct mode. The source keeps alternate register structs for different SPEAr layouts, but the match table only lists `st,spear600-adc`.

## Risks
`wait_for_completion()` in `spear_adc_read_raw()` has no timeout, so a missed IRQ can block indefinitely. Completion is initialized once and not reinitialized per conversion, which risks stale completions on repeated reads. `spear_adc_set_status()` always writes through the SPEAr6xx pointer, while some helpers branch by compatible for readback; this is acceptable for current match data but fragile if older compatibles are reintroduced.

## Test signals
Test missing required sampling-frequency property, sample-frequency writes at min/max/out of range, repeated raw reads, IRQ failure or missing completion behavior, internal versus external VREF scale, average-samples property effects, and register layout assumptions for compatible additions.
