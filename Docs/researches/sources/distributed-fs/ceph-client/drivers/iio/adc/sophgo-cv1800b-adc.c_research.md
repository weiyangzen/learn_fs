# sources/distributed-fs/ceph-client/drivers/iio/adc/sophgo-cv1800b-adc.c

## Purpose
This platform IIO driver supports the Sophgo CV1800B SAR ADC. It exposes three voltage channels with raw conversion, fixed 3.3 V 12-bit scale, and computed sample frequency.

## Important APIs, types, and functions
`struct cv1800b_adc` stores completion, MMIO registers, mutex, clock, and optional IRQ. The key paths are `cv1800b_adc_start_measurement()`, `cv1800b_adc_wait()`, `cv1800b_adc_read_raw()`, `cv1800b_adc_interrupt_handler()`, and `cv1800b_adc_probe()`.

## Control flow
Probe allocates IIO state, enables the clock, maps registers, optionally requests an IRQ and enables ADC interrupts, initializes the mutex, programs startup/sample/clock-divider/compare cycle settings, and registers IIO. A raw read locks the ADC, clears the control register, starts one selected channel, waits either by polling busy status or by completion from IRQ, reads the channel result register, unlocks, checks the valid bit, and returns the 12-bit sample.

## State and persistence
Cycle timing configuration is programmed at probe and then read back for sample-frequency reporting. There is no runtime PM or cached conversion state. Completion is used only when an IRQ is available; otherwise polling is used.

## Dependencies and integration points
The driver depends on a platform MMIO resource, an enabled clock, optional IRQ, IIO direct mode, and compatible `sophgo,cv1800b-saradc`.

## Risks
There is no runtime PM or explicit ADC disable after conversion beyond writing control for the next read. If an IRQ is present, the code does not reinitialize the completion before each conversion, so a stale completion could allow an immediate read of an old or invalid sample after the first interrupt. Sample frequency calculation divides by the programmed cycle fields but does not guard against a zero clock rate.

## Test signals
Test both IRQ and polling modes, repeated IRQ-backed reads for stale completion behavior, invalid result bit handling, sample-frequency math from cycle settings, clock failure, timeout handling, and concurrent reads serialized by the mutex.
