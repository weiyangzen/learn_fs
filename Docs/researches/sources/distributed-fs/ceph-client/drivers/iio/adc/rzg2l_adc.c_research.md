# sources/distributed-fs/ceph-client/drivers/iio/adc/rzg2l_adc.c

## Purpose
This platform IIO driver supports Renesas RZ/G2L-family ADCs, including the RZ/G2L 8-channel variant and RZ/G3S 9-channel variant with a temperature input. It provides direct raw conversion reads and channel labels.

## Important APIs, types, and functions
`struct rzg2l_adc_hw_params` captures variant-specific sampling-period masks, default sampling values, interrupt masks, number of channels, comparator defaults, and optional ADIVC clock divider support. `struct rzg2l_adc` holds MMIO base, reset controls, parsed channel data, completion, mutex, and last conversion values. Key routines are `rzg2l_adc_conversion_setup()`, `rzg2l_adc_conversion()`, `rzg2l_adc_read_raw()`, `rzg2l_adc_isr()`, `rzg2l_adc_hw_init()`, and runtime/system PM callbacks.

## Control flow
Probe selects hardware parameters from the compatible, parses firmware channel children with `devm_iio_adc_device_alloc_chaninfo_se()`, maps registers, deasserts resets, enables runtime PM, initializes hardware, requests the conversion IRQ, and registers IIO. A raw read resumes the device, configures software-trigger select mode for one channel, programs channel selection and sampling period, enables channel-select-error and conversion interrupts, starts conversion, waits for completion, stops conversion, and returns `last_val[channel]` filled by the ISR.

## State and persistence
The driver stores only transient conversion results in `last_val[]`; most hardware configuration is reconstructed on each conversion or in `rzg2l_adc_hw_init()`. Runtime suspend powers down the analog block with `PWDWNB`; system suspend force-suspends PM and asserts resets. Resume deasserts resets, force-resumes PM, and reinitializes ADC registers.

## Dependencies and integration points
Dependencies include platform MMIO, reset controls named `adrst-n` and `presetn`, runtime PM, IRQ completion, IIO ADC firmware helpers, and device-tree compatibles `renesas,rzg2l-adc` and `renesas,r9a08g045-adc`.

## Risks
The timeout is extremely short (`usecs_to_jiffies(4)`), so low HZ configurations can make timeout semantics coarse and hardware latency assumptions fragile. Conversion setup returns `-EBUSY` if hardware reports busy. Channel-select error interrupts are acknowledged but do not complete the waiting conversion, so the caller times out. Since only direct reads are implemented, no buffered path exercises scan ordering.

## Test signals
Exercise probe on both variants, firmware channel validation above max channel count, voltage and temperature labels, raw read success, busy ADC behavior, timeout path that masks interrupts and stops conversion, reset/system PM resume reinitialization, and ADIVC programming only on variants that support it.
