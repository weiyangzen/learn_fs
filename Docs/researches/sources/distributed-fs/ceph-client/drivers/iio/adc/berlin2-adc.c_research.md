# sources/distributed-fs/ceph-client/drivers/iio/adc/berlin2-adc.c

## Purpose
This Marvell Berlin2 driver exposes system-manager ADC channels through IIO. It provides raw voltage reads for external/reserved ADC inputs and a processed temperature channel using the integrated temperature sensor. It is direct-mode only and uses separate ADC and temperature-sensor IRQs.

## Important APIs, Types, And Functions
`struct berlin2_adc_priv` stores the parent syscon regmap, a mutex, waitqueue, `data_available`, and captured data. `berlin2_adc_read()` performs single ADC conversions. `berlin2_adc_tsen_read()` performs temperature-sensor conversions. `berlin2_adc_read_raw()` dispatches raw voltage and processed temperature reads. `berlin2_adc_irq()` and `berlin2_adc_tsen_irq()` capture data-ready values and wake waiters. `berlin2_adc_powerdown()` is a devm cleanup action.

## Control Flow
Probe gets the parent node regmap, requests named IRQs `adc` and `tsen`, initializes waitqueue/mutex, sets IIO metadata, powers the ADC by setting `BERLIN2_SM_CTRL_ADC_POWER`, registers a cleanup action to power it down, and registers the IIO device. A voltage read enables the channel interrupt, selects the ADC channel, starts conversion, waits up to one second for `data_available`, disables the interrupt, clears start, copies the latched data, and returns it. A temperature read enables TSEN interrupt, configures ADC rotate and TSEN trim/settling/start, waits similarly, stops TSEN, sign-adjusts the 12-bit-ish value when over 2047, and converts it to milli-Celsius.

## State And Persistence
There is no persistent state. `data_available` and `data` are shared by ADC and TSEN paths and serialized with `priv->lock`, preventing simultaneous reads. Hardware ADC power remains on while the driver is bound and is cleared by devm cleanup.

## Dependencies And Integration Points
The driver integrates with OF compatible `marvell,berlin2-adc`, platform named IRQs, parent syscon regmap, IIO core, and waitqueues. The channel table includes six voltage-ish channel numbers, one processed temperature channel, one reserved voltage channel, and a soft timestamp channel even though no buffer setup is provided.

## Risks And Test Signals
Risks include shared `data_available` state across two IRQ sources, raw channel table exposing reserved channels, no scale for voltage channels, reliance on parent-node syscon layout, and no explicit handling of interrupted waits beyond propagating negative return. Test signals include named IRQ availability, ADC power cleanup on probe failure/remove, raw conversion timeout, TSEN conversion formula sanity, and no cross-talk between concurrent voltage and temperature reads under the mutex.
