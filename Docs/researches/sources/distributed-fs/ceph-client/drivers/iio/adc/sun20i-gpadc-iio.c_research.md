# sources/distributed-fs/ceph-client/drivers/iio/adc/sun20i-gpadc-iio.c

Purpose: direct-mode IIO GPADC driver for newer Allwinner sunxi platforms such as D1, T113-S3, and R329. It provides raw voltage channels allocated from firmware ADC channel info and a fixed 1.8 V / 12-bit scale.

Important APIs/types/functions: `struct sun20i_gpadc_iio` holds MMIO registers, completion, last selected channel, and a read mutex. Key routines are `sun20i_gpadc_adc_read()`, `sun20i_gpadc_read_raw()`, `sun20i_gpadc_irq_handler()`, `sun20i_gpadc_alloc_channels()`, and probe.

Control flow: probe allocates an IIO device, parses channel descriptors via `devm_iio_adc_device_alloc_chaninfo_se()`, maps registers, enables the bus clock, deasserts reset with a devm cleanup action, requests IRQ, programs autocalibration and single-conversion work mode, then registers IIO. A raw read serializes access, programs channel enable and data IRQ when the channel changes, enables ADC conversion, waits up to 10 ms for data interrupt, reads the per-channel data register, and unlocks. IRQ clears all data interrupt status and completes the pending read.

State and persistence: persistent software state is the MMIO pointer and `last_channel` cache used to avoid repeated channel/IRQ programming. Hardware state includes selected channel mask, data interrupt enable, CTRL autocalibration/single-mode/ADC-enable bits, reset line, and clock enable.

Dependencies and integration: depends on platform MMIO/IRQ, clock and reset frameworks, firmware property-based IIO ADC channel allocation, IIO direct mode, and Allwinner compatible `allwinner,sun20i-d1-gpadc`.

Risks: IRQ handler completes on any data interrupt after clearing all status bits, so concurrent reads are correctly serialized by the mutex but spurious interrupts may complete a read early. ADC enable is not explicitly cleared after each read. Timeout assumptions rely on datasheet acquisition/conversion maximums. Only scale is fixed; no calibration result is surfaced.

Test signals: firmware-defined channel enumeration, channel-switch reads, timeout with masked IRQ, interrupt status clearing, reset assertion cleanup, clock-enable failure, fixed scale reporting, and repeated reads that use `last_channel`.
