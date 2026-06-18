# sources/distributed-fs/ceph-client/drivers/iio/adc/imx8qxp-adc.c

## Purpose
`imx8qxp-adc.c` is the direct-mode IIO driver for the NXP i.MX8QuadXPlus ADC. It exposes eight voltage channels and uses software-triggered single conversions with FIFO watermark interrupts.

## Important APIs, types, and functions
- `struct imx8qxp_adc` stores MMIO, peripheral and IPG clocks, `vref`, mutex, completion, and a small FIFO cache.
- `imx8qxp_adc_reset()` performs software reset and FIFO reset.
- `imx8qxp_adc_reg_config()` configures ADC power/reference, trigger 0, command low/high fields, averaging, and channel selection.
- `imx8qxp_adc_fifo_config()` sets FIFO watermark and interrupt enable.
- `imx8qxp_adc_read_raw()` uses runtime PM, configures a conversion, enables the ADC, writes `SWTRIG`, and waits for completion.
- Runtime PM callbacks enable/disable regulator and both clocks and reset or disable the ADC.

## Control flow
Probe maps resources, gets IRQ, `per` and `ipg` clocks, enables `vref`, prepares/enables clocks, requests the IRQ, resets hardware, registers IIO, and enables runtime autosuspend. A raw read resumes the device, locks, configures channel and FIFO, starts conversion, waits up to 100 ms, then returns `fifo[0]` and schedules autosuspend.

## State and persistence
Runtime state is limited to power/clock state, current register configuration, and last FIFO samples. There is no persistent setting beyond hardware registers. Runtime suspend powers down the ADC by disabling it, clocks, and regulator.

## Dependencies and integration points
The driver uses platform/OF `nxp,imx8qxp-adc`, MMIO, IRQs, completions, common clocks, regulator consumers, runtime PM autosuspend, and IIO debugfs register access.

## Risks
- `pm_runtime_get_sync()` return values are not checked; failed resume could still proceed into register access.
- IRQ handler trusts FIFO count up to hardware maximum; mismatched masks could overrun `fifo`.
- Conversion start and runtime PM put occur before timeout checks, so failure paths depend on autosuspend behavior.

## Test signals
Validate runtime PM resume/suspend, raw reads for all channels, FIFO count handling, scale from `vref`, sample frequency from `per` clock, debugfs register reads, and timeout behavior when the IRQ is absent.
